"""Recalcul indépendant de solidarites.taux_pauvrete_erfs (INSEE ERFS rétropolé)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "insee-erfs-retropole.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select GEO, EMPSTA_ENQ, AGE, TPH, MUN_DENSITY_LEVEL, TIME_PERIOD, OBS_VALUE "
        f"from read_parquet('{FICHIER.as_posix()}') where ERFS_MEASURE = 'PR_MD60'"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["GEO"] != "FM":
            continue
        if ligne["EMPSTA_ENQ"] != "_T" or ligne["AGE"] != "_T" or ligne["TPH"] != "_T" or ligne["MUN_DENSITY_LEVEL"] != "_T":
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue

        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France métropolitaine",
                "periode": ligne["TIME_PERIOD"],
                "valeur": float(ligne["OBS_VALUE"]),
            }
        )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
