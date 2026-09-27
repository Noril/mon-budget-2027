"""Recalcul indépendant de solidarites.depense_protection_sociale.

Eurostat spr_exp_type : dépenses totales de protection sociale en % du PIB.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-spr-exp-type.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select spdeps, unit, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["spdeps"].split(":")[0] != "TOTAL":
            continue
        if ligne["unit"].split(":")[0] != "PC_GDP":
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
