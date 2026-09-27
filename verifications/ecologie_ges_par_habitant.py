"""Recalcul indépendant de ecologie.ges_par_habitant.

Numérateur : Eurostat env_air_gge, unit = MIO_T, airpol = GHG, src_crf = TOTX4_MEMO (millions de tonnes).
Dénominateur : Eurostat demo_gind (population moyenne), indic_de = AVG. Valeur = 10^6 * émissions / population,
arrondie à 0,01, pour les seuls couples (pays, année) présents dans les deux jeux.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_GES = NORMALISE / "eurostat-env-air-gge.parquet"
FICHIER_POP = NORMALISE / "eurostat-population-moyenne.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    emissions: dict[tuple[str, str], tuple[float, str]] = {}
    for ligne in _lignes(FICHIER_GES):
        if not ligne["unit"].startswith("MIO_T:"):
            continue
        if not ligne["airpol"].startswith("GHG:"):
            continue
        if not ligne["src_crf"].startswith("TOTX4_MEMO:"):
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue
        code, libelle = _code_libelle(ligne["geo"])
        emissions[(code, ligne["TIME_PERIOD"])] = (float(ligne["OBS_VALUE"]), libelle)

    population: dict[tuple[str, str], float] = {}
    for ligne in _lignes(FICHIER_POP):
        if not ligne["indic_de"].startswith("AVG:"):
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue
        code, _ = _code_libelle(ligne["geo"])
        population[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    resultat: list[dict] = []
    for (code, periode), (emission, libelle) in emissions.items():
        pop = population.get((code, periode))
        if pop is None or pop == 0:
            continue
        valeur = arrondi(10**6 * emission / pop, 2)
        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
