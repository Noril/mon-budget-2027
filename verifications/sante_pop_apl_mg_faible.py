"""Recalcul indépendant de sante.pop_apl_mg_faible à partir des Parquet normalisés.

Démarche volontairement différente d'une requête SQL agrégée : les lignes brutes de
drees-apl.parquet sont lues une par une et classées/accumulées en Python (règles
explicites), sans GROUP BY / JOIN SQL. Règles déduites en explorant les données (pas
les formules SQL du pipeline) :

- Seuil : "inférieure à 2,5" est pris au sens strict (apl < 2,5). 43 lignes ont une
  valeur d'APL exactement égale à 2,5 dans les données ; les inclure (apl <= 2,5)
  change le résultat de façon visible (testé sur les départements 03/25/56 en 2022),
  donc la convention stricte/large n'est pas anodine — voir l'ambiguïté signalée.
- Population : pop_totale (non standardisée), comme l'indique le champ `limites`.
- Département / région : part de la population des communes de drees-apl vivant sous
  le seuil, parmi les communes rattachées à un département/région du COG. Comme pour
  sante.apl_mg, les lignes TYPECOM = COMD/COMA d'insee-cog-communes ont DEP/REG à
  NULL et doivent être rattachées via COMPARENT (en chaîne si besoin) jusqu'à une
  ligne COM/ARM ; 69 codes commune de drees-apl ne sont retrouvés QUE comme COMD/COMA.
  12 codes commune de drees-apl restent introuvables dans le COG 2026 (communes
  fusionnées/supprimées depuis) et sont exclus de ces agrégats.
- France : calculée sur TOUTES les lignes de drees-apl (y compris les 12 codes non
  retrouvés dans le COG) — pas besoin du COG à cette maille. Mayotte est absente de
  drees-apl, donc hors champ nativement.
- Arrondi : constaté empiriquement à 2 décimales pour toutes les mailles (le champ
  `format` du YAML, "{:.1f} %", ne décrit que l'affichage, pas la précision stockée).
- Pas de maille commune pour cet indicateur (cohérent avec `maille` du YAML, qui
  n'inclut pas "commune" — c'est un indicateur de part de population, pas de valeur
  ponctuelle).
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_APL = NORMALISE / "drees-apl.parquet"
FICHIER_COMMUNES = NORMALISE / "insee-cog-communes.parquet"

SEUIL_APL = 2.5
ARRONDI = 2


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
    """Population totale, et population sous le seuil, pour calculer une part à la fin."""

    def __init__(self) -> None:
        self.population_totale = 0.0
        self.population_sous_seuil = 0.0

    def ajouter(self, apl: float, population: float) -> None:
        self.population_totale += population
        if apl < SEUIL_APL:
            self.population_sous_seuil += population

    def part(self) -> float | None:
        if self.population_totale == 0:
            return None
        return round(100.0 * self.population_sous_seuil / self.population_totale, ARRONDI)


def calculer() -> list[dict]:
    com_vers_dep_reg = _commune_vers_dep_reg()

    par_departement: dict[tuple[str, str], _Accumulateur] = {}
    par_region: dict[tuple[str, str], _Accumulateur] = {}
    par_france: dict[str, _Accumulateur] = {}

    for ligne in _lignes(FICHIER_APL):
        annee = ligne["annee"]
        code_commune = ligne["code_commune"]
        apl = ligne["apl"]
        population = ligne["pop_totale"]

        if apl is None or population is None:
            continue  # aucune ligne masquée constatée dans les données, mais on ne suppose rien

        par_france.setdefault(annee, _Accumulateur()).ajouter(apl, population)

        correspondance = com_vers_dep_reg.get(code_commune)
        if correspondance is None:
            continue
        dep, reg = correspondance
        par_departement.setdefault((dep, annee), _Accumulateur()).ajouter(apl, population)
        par_region.setdefault((reg, annee), _Accumulateur()).ajouter(apl, population)

    resultat: list[dict] = []

    for (dep, annee), acc in par_departement.items():
        valeur = acc.part()
        if valeur is not None:
            resultat.append({"maille": "departement", "code": dep, "periode": annee, "valeur": valeur})

    for (reg, annee), acc in par_region.items():
        valeur = acc.part()
        if valeur is not None:
            resultat.append({"maille": "region", "code": reg, "periode": annee, "valeur": valeur})

    for annee, acc in par_france.items():
        valeur = acc.part()
        if valeur is not None:
            resultat.append({"maille": "france", "code": "FR", "periode": annee, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
