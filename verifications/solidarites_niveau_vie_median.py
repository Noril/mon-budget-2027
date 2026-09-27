"""Recalcul indépendant de solidarites.niveau_vie_median.

Filosofi (Melodi DS_FILOSOFI_CC), mesure MED_SL (niveau de vie médian), mailles
france / region / departement.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "insee-filosofi.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select GEO, GEO_OBJECT, CONF_STATUS, TIME_PERIOD, OBS_VALUE "
        f"from read_parquet('{FICHIER.as_posix()}') where FILOSOFI_MEASURE = 'MED_SL'"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["CONF_STATUS"] == "C":
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue

        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]
        objet, geo = ligne["GEO_OBJECT"], ligne["GEO"]

        if objet == "FRANCE" and geo == "FM":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France métropolitaine", "periode": periode, "valeur": valeur})
        elif objet == "REG":
            resultat.append({"maille": "region", "code": geo, "libelle": geo, "periode": periode, "valeur": valeur})
        elif objet == "DEP":
            resultat.append({"maille": "departement", "code": geo, "libelle": geo, "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
