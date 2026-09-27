"""Recalcul indépendant de energie.prix_electricite_menages à partir d'Eurostat nrg_pc_204."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "eurostat-nrg-pc-204.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not (
            ligne["siec"].startswith("E7000")
            and ligne["nrg_cons"].startswith("KWH2500-4999")
            and ligne["unit"].startswith("KWH")
            and ligne["tax"].startswith("I_TAX")
            and ligne["currency"].startswith("EUR")
        ):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")
        valeur = arrondi(100 * float(ligne["OBS_VALUE"]), 2)
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
