"""Recalcul indépendant de numerique.emploi_informatique.

Source urssaf-effectifs-informatique (déjà filtrée sur les codes APE 62/63), une colonne effectifs_salaries_AAAA
par année, une ligne par commune et code APE. Rattachement de code_commune au département et à la région par
le COG 2026 (insee-cog-communes) : TYPECOM COM ou ARM porte DEP/REG directement ; COMD et COMA héritent de leur
COMPARENT ; un code présent en COM et en COMD prend la ligne COM. Valeur = somme des effectifs (cellules vides
ignorées), sans arrondi. Maille France : toutes les lignes (rattachées ou non).
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_URSSAF = NORMALISE / "urssaf-effectifs-informatique.parquet"
FICHIER_COG_COMMUNES = NORMALISE / "insee-cog-communes.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"
FICHIER_COG_REG = NORMALISE / "insee-cog-regions.parquet"

ANNEES = [str(a) for a in range(2006, 2026)]


def _lignes(fichier, colonnes="*") -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select {colonnes} from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in curseur.description]
    return [dict(zip(cols, ligne)) for ligne in curseur.fetchall()]


def _rattachement_communes() -> dict[str, tuple[str, str]]:
    lignes = _lignes(FICHIER_COG_COMMUNES, "TYPECOM, COM, DEP, REG, COMPARENT")
    rattache: dict[str, tuple[str, str]] = {}
    # priorité aux lignes COM/ARM (portent directement DEP et REG)
    for l in lignes:
        if l["TYPECOM"] in ("COM", "ARM") and l["DEP"] is not None:
            rattache[l["COM"]] = (l["DEP"], l["REG"])
    # COMD/COMA héritent de leur COMPARENT, seulement si le code n'a pas déjà une ligne COM/ARM
    for l in lignes:
        if l["TYPECOM"] in ("COMD", "COMA") and l["COM"] not in rattache:
            parent = rattache.get(l["COMPARENT"])
            if parent is not None:
                rattache[l["COM"]] = parent
    return rattache


def _libelles_dep() -> dict[str, str]:
    return {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG_DEP, "DEP, LIBELLE")}


def _libelles_reg() -> dict[str, str]:
    return {l["REG"]: l["LIBELLE"] for l in _lignes(FICHIER_COG_REG, "REG, LIBELLE")}


def calculer() -> list[dict]:
    rattache = _rattachement_communes()
    libelles_dep = _libelles_dep()
    libelles_reg = _libelles_reg()

    colonnes_effectifs = ", ".join(f"effectifs_salaries_{a}" for a in ANNEES)
    lignes = _lignes(FICHIER_URSSAF, f"code_commune, {colonnes_effectifs}")

    somme_dep: dict[tuple[str, str], int] = {}
    somme_reg: dict[tuple[str, str], int] = {}
    somme_france: dict[str, int] = {}

    for l in lignes:
        cle_commune = l["code_commune"]
        dep_reg = rattache.get(cle_commune)
        for annee in ANNEES:
            effectif = l[f"effectifs_salaries_{annee}"]
            if effectif is None:
                continue
            somme_france[annee] = somme_france.get(annee, 0) + effectif
            if dep_reg is not None:
                dep, reg = dep_reg
                somme_dep[(dep, annee)] = somme_dep.get((dep, annee), 0) + effectif
                somme_reg[(reg, annee)] = somme_reg.get((reg, annee), 0) + effectif

    resultat: list[dict] = []
    for (dep, annee), valeur in somme_dep.items():
        resultat.append({"maille": "departement", "code": dep, "libelle": libelles_dep.get(dep, dep), "periode": annee, "valeur": float(valeur)})
    for (reg, annee), valeur in somme_reg.items():
        resultat.append({"maille": "region", "code": reg, "libelle": libelles_reg.get(reg, reg), "periode": annee, "valeur": float(valeur)})
    for annee, valeur in somme_france.items():
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": float(valeur)})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
