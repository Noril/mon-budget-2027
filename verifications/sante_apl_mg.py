"""Recalcul indépendant de sante.apl_mg à partir des Parquet normalisés.

Démarche volontairement différente d'une requête SQL agrégée : les lignes brutes de
drees-apl.parquet sont lues une par une et accumulées dans des dictionnaires Python
(règles explicites), sans GROUP BY / JOIN SQL. Les règles ont été déduites en explorant
les données (pas les formules SQL du pipeline) :

- Commune : la valeur APL de la DREES est reprise telle quelle (elle a déjà au plus
  3 décimales dans la source).
- Département / région : moyenne de l'APL pondérée par la population standardisée,
  sur les communes de drees-apl rattachées à un département/région du COG. Piège
  constaté en explorant les données (note du catalogue sur insee-cog-communes) :
  les lignes TYPECOM = COMD (communes déléguées) et COMA (associées) ont DEP/REG à
  NULL dans insee-cog-communes et doivent être rattachées via COMPARENT (parfois en
  chaîne) jusqu'à une ligne COM ou ARM porteuse d'un DEP/REG ; 69 codes commune de
  drees-apl ne sont retrouvés QUE comme COMD/COMA (pas de ligne COM/ARM avec le même
  code) et ont besoin de cette résolution. Les arrondissements de Paris/Lyon/Marseille
  (TYPECOM = ARM), eux, portent déjà un DEP/REG en direct. 12 codes commune de
  drees-apl restent malgré tout introuvables dans le COG 2026 (communes fusionnées/
  supprimées depuis) et sont mécaniquement exclus des agrégats départementaux et
  régionaux, tout en restant dans les valeurs communales.
- France : moyenne pondérée par la population standardisée sur TOUTES les lignes de
  drees-apl (y compris les 12 codes non retrouvés dans le COG) — la maille France n'a
  pas besoin du COG. Mayotte est absente de drees-apl, donc hors champ nativement.
- Arrondi : constaté empiriquement à 3 décimales pour toutes les mailles (le champ
  `format` du YAML, "{:.1f} ...", ne décrit que l'affichage, pas la précision stockée
  — voir l'ambiguïté signalée dans le rapport).
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_APL = NORMALISE / "drees-apl.parquet"
FICHIER_COMMUNES = NORMALISE / "insee-cog-communes.parquet"

ARRONDI = 3


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _commune_vers_dep_reg() -> dict[str, tuple[str, str]]:
    """code commune -> (departement, region), résolu via le COG.

    Les lignes COM/ARM portent directement DEP/REG. Les lignes COMD/COMA n'en
    portent pas : on suit alors COMPARENT (au besoin en chaîne) jusqu'à retrouver
    une ligne COM/ARM. Un code absent du COG (communes fusionnées/supprimées depuis)
    reste sans correspondance.
    """
    lignes_par_code: dict[str, list[dict]] = {}
    for ligne in _lignes(FICHIER_COMMUNES):
        lignes_par_code.setdefault(ligne["COM"], []).append(ligne)

    memo: dict[str, tuple[str, str] | None] = {}

    def resoudre(code: str, profondeur: int = 0) -> tuple[str, str] | None:
        if code in memo:
            return memo[code]
        if profondeur > 10:
            return None
        memo[code] = None  # garde-fou anti-cycle pendant la résolution
        candidats = lignes_par_code.get(code, [])
        for c in candidats:
            if c["TYPECOM"] in ("COM", "ARM") and c["DEP"] is not None:
                memo[code] = (c["DEP"], c["REG"])
                return memo[code]
        for c in candidats:
            parent = c["COMPARENT"]
            if parent and parent != code:
                resultat = resoudre(parent, profondeur + 1)
                if resultat is not None:
                    memo[code] = resultat
                    return resultat
        return None

    return {code: resoudre(code) for code in lignes_par_code}


class _Accumulateur:
    """Somme (apl * poids) et somme(poids), pour calculer une moyenne pondérée à la fin."""

    def __init__(self) -> None:
        self.numerateur = 0.0
        self.denominateur = 0.0

    def ajouter(self, apl: float, poids: float) -> None:
        self.numerateur += apl * poids
        self.denominateur += poids

    def moyenne(self) -> float | None:
        if self.denominateur == 0:
            return None
        return round(self.numerateur / self.denominateur, ARRONDI)


def calculer() -> list[dict]:
    com_vers_dep_reg = _commune_vers_dep_reg()

    resultat: list[dict] = []
    par_departement: dict[tuple[str, str], _Accumulateur] = {}
    par_region: dict[tuple[str, str], _Accumulateur] = {}
    par_france: dict[str, _Accumulateur] = {}

    for ligne in _lignes(FICHIER_APL):
        annee = ligne["annee"]
        code_commune = ligne["code_commune"]
        apl = ligne["apl"]
        poids = ligne["pop_standardisee"]

        if apl is None or poids is None:
            continue  # aucune ligne masquée constatée dans les données, mais on ne suppose rien

        # -- maille commune : valeur brute de la DREES, sans transformation.
        resultat.append(
            {
                "maille": "commune",
                "code": code_commune,
                "libelle": ligne["commune"],
                "periode": annee,
                "valeur": round(apl, ARRONDI),
            }
        )

        # -- maille France : sur toutes les lignes, COG ou pas.
        par_france.setdefault(annee, _Accumulateur()).ajouter(apl, poids)

        # -- mailles département / région : seulement si la commune est retrouvée au COG.
        correspondance = com_vers_dep_reg.get(code_commune)
        if correspondance is None:
            continue
        dep, reg = correspondance
        par_departement.setdefault((dep, annee), _Accumulateur()).ajouter(apl, poids)
        par_region.setdefault((reg, annee), _Accumulateur()).ajouter(apl, poids)

    for (dep, annee), acc in par_departement.items():
        valeur = acc.moyenne()
        if valeur is not None:
            resultat.append({"maille": "departement", "code": dep, "periode": annee, "valeur": valeur})

    for (reg, annee), acc in par_region.items():
        valeur = acc.moyenne()
        if valeur is not None:
            resultat.append({"maille": "region", "code": reg, "periode": annee, "valeur": valeur})

    for annee, acc in par_france.items():
        valeur = acc.moyenne()
        if valeur is not None:
            resultat.append({"maille": "france", "code": "FR", "periode": annee, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
