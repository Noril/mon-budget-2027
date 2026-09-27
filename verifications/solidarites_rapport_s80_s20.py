"""Recalcul indépendant de solidarites.rapport_s80_s20 (Eurostat ilc_di11)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-ilc-di11.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select age, sex, unit, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["age"].split(":")[0] != "TOTAL":
            continue
        if ligne["sex"].split(":")[0] != "T":
            continue
        if ligne["unit"].split(":")[0] != "RAT":
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue

        code, _, libelle = ligne["geo"].partition(":")
        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
