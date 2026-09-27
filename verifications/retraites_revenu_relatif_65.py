"""Recalcul indépendant de retraites.revenu_relatif_65 (Eurostat ilc_pnp2)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-ilc-pnp2.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select statinfo, age, sex, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["statinfo"].split(":")[0] != "R_MED_I":
            continue
        if ligne["age"].split(":")[0] != "Y_GE65":
            continue
        if ligne["sex"].split(":")[0] != "T":
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue

        code, _, libelle = ligne["geo"].partition(":")
        valeur = round(100 * float(ligne["OBS_VALUE"]), 1)
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
