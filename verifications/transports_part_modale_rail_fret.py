"""Recalcul indépendant de transports.part_modale_rail_fret à partir d'Eurostat tran_hv_frmod."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-tran-hv-frmod.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not (ligne["tra_mode"].partition(":")[0] == "RAIL" and ligne["unit"].startswith("PC")):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")
        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
