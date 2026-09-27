"""Recalcul indépendant de ecologie.tues_route.

Deux calculs indépendants (champs différents, non recopiés l'un sur l'autre) :
- départements et France : onisr-baac (tués par année et département) / population au 1er janvier du même
  département et de la même année (insee-estimations-population), pour les départements présents dans le COG
  des départements (Mayotte incluse, autres COM/DOM exclus). France = somme des tués / somme des populations
  des départements gardés.
- pays (dont FR) : Eurostat tran_sf_roadus (NR, sex=T, age=TOTAL, pers_cat=TOTAL) / population moyenne
  (demo_gind, indic_de=AVG) du même pays et de la même année.
Valeur = 10^6 * tués / population, arrondie à 0,1.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_ONISR = NORMALISE / "onisr-baac.parquet"
FICHIER_POP_DEP = NORMALISE / "insee-estimations-population.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"
FICHIER_TUES_PAYS = NORMALISE / "eurostat-tran-sf-roadus.parquet"
FICHIER_POP_PAYS = NORMALISE / "eurostat-population-moyenne.parquet"


def _lignes(fichier, colonnes="*") -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select {colonnes} from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in curseur.description]
    return [dict(zip(cols, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def _departements_et_france() -> list[dict]:
    deps_cog = {l["DEP"] for l in _lignes(FICHIER_COG_DEP, "DEP")}

    population: dict[tuple[str, str], float] = {}
    for l in _lignes(FICHIER_POP_DEP, "GEO_OBJECT, EP_MEASURE, AGE, SEX, GEO, TIME_PERIOD, OBS_VALUE"):
        if l["GEO_OBJECT"] != "DEP" or l["EP_MEASURE"] != "POP_JAN_1ST" or l["AGE"] != "_T" or l["SEX"] != "_T":
            continue
        if l["OBS_VALUE"] is None or l["OBS_VALUE"] == "":
            continue
        population[(l["GEO"], l["TIME_PERIOD"])] = float(l["OBS_VALUE"])

    resultat: list[dict] = []
    par_annee_tues: dict[str, float] = {}
    par_annee_pop: dict[str, float] = {}
    for l in _lignes(FICHIER_ONISR, "annee, dep, tues"):
        if l["dep"] not in deps_cog:
            continue
        pop = population.get((l["dep"], l["annee"]))
        if pop is None or pop == 0:
            continue
        valeur = arrondi(10**6 * l["tues"] / pop, 1)
        resultat.append({"maille": "departement", "code": l["dep"], "libelle": l["dep"], "periode": l["annee"], "valeur": valeur})
        par_annee_tues[l["annee"]] = par_annee_tues.get(l["annee"], 0.0) + l["tues"]
        par_annee_pop[l["annee"]] = par_annee_pop.get(l["annee"], 0.0) + pop

    for annee, tues in par_annee_tues.items():
        pop = par_annee_pop[annee]
        valeur = arrondi(10**6 * tues / pop, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": valeur})
    return resultat


def _pays() -> list[dict]:
    population: dict[tuple[str, str], float] = {}
    for l in _lignes(FICHIER_POP_PAYS, "indic_de, geo, TIME_PERIOD, OBS_VALUE"):
        if not l["indic_de"].startswith("AVG:"):
            continue
        if l["OBS_VALUE"] is None or l["OBS_VALUE"] == "":
            continue
        code, _ = _code_libelle(l["geo"])
        population[(code, l["TIME_PERIOD"])] = float(l["OBS_VALUE"])

    resultat: list[dict] = []
    for l in _lignes(FICHIER_TUES_PAYS, "sex, age, unit, pers_cat, geo, TIME_PERIOD, OBS_VALUE"):
        if not l["unit"].startswith("NR:"):
            continue
        if not l["sex"].startswith("T:"):
            continue
        if not l["age"].startswith("TOTAL:"):
            continue
        if not l["pers_cat"].startswith("TOTAL:"):
            continue
        if l["OBS_VALUE"] is None or l["OBS_VALUE"] == "":
            continue
        code, libelle = _code_libelle(l["geo"])
        pop = population.get((code, l["TIME_PERIOD"]))
        if pop is None or pop == 0:
            continue
        valeur = arrondi(10**6 * float(l["OBS_VALUE"]) / pop, 1)
        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": l["TIME_PERIOD"], "valeur": valeur})
    return resultat


def calculer() -> list[dict]:
    return _departements_et_france() + _pays()


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
