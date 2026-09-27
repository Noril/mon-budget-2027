"""Recalcul indépendant de logement.logements_autorises.

Source sdes-sitadel-departements, lignes TYPE_LGT = "Tous Logements", colonne LOG_AUT sommée sur les douze
mois de l'année civile ; seules les années dont les douze mois figurent (par département) sont retenues.
Dénominateur : insee-estimations-population, GEO_OBJECT = DEP, EP_MEASURE = POP_JAN_1ST, AGE = _T, SEX = _T.
Valeur = 1000 * logements / population, arrondie à 0,01. France = somme des logements des départements
retenus / somme de leurs populations.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_SITADEL = NORMALISE / "sdes-sitadel-departements.parquet"
FICHIER_POP = NORMALISE / "insee-estimations-population.parquet"

COLONNE = "LOG_AUT"


def _lignes(fichier, colonnes="*") -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select {colonnes} from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in curseur.description]
    return [dict(zip(cols, ligne)) for ligne in curseur.fetchall()]


def _population() -> dict[tuple[str, str], float]:
    population = {}
    for l in _lignes(FICHIER_POP, "GEO_OBJECT, EP_MEASURE, AGE, SEX, GEO, TIME_PERIOD, OBS_VALUE"):
        if l["GEO_OBJECT"] != "DEP" or l["EP_MEASURE"] != "POP_JAN_1ST" or l["AGE"] != "_T" or l["SEX"] != "_T":
            continue
        if l["OBS_VALUE"] in (None, ""):
            continue
        population[(l["GEO"], l["TIME_PERIOD"])] = float(l["OBS_VALUE"])
    return population


def calculer() -> list[dict]:
    lignes = [l for l in _lignes(FICHIER_SITADEL, f"ANNEE, MOIS, DEPARTEMENT_CODE, TYPE_LGT, {COLONNE}") if l["TYPE_LGT"] == "Tous Logements"]

    mois_presents: dict[tuple[str, str], set[str]] = {}
    for l in lignes:
        mois_presents.setdefault((l["DEPARTEMENT_CODE"], l["ANNEE"]), set()).add(l["MOIS"])
    territoires_retenus = {cle for cle, mois in mois_presents.items() if len(mois) == 12}

    somme_dep: dict[tuple[str, str], float] = {}
    for l in lignes:
        cle = (l["DEPARTEMENT_CODE"], l["ANNEE"])
        if cle not in territoires_retenus:
            continue
        valeur = l[COLONNE]
        if valeur in (None, ""):
            continue
        somme_dep[cle] = somme_dep.get(cle, 0.0) + float(valeur)

    population = _population()

    resultat: list[dict] = []
    somme_france: dict[str, list[float]] = {}
    for (dep, annee), logements in somme_dep.items():
        pop = population.get((dep, annee))
        if pop is None or pop == 0:
            continue
        resultat.append({"maille": "departement", "code": dep, "libelle": dep, "periode": annee, "valeur": arrondi(1000 * logements / pop, 2)})
        somme_france.setdefault(annee, [0.0, 0.0])
        somme_france[annee][0] += logements
        somme_france[annee][1] += pop

    for annee, (logements, pop) in somme_france.items():
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": arrondi(1000 * logements / pop, 2)})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
