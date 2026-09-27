"""Recalcul indépendant de transports.regularite_tgv à partir de sncf-regularite-tgv.

Moyenne arithmétique simple des douze valeurs mensuelles de regularite_composite ;
années à moins de douze mois exclues.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "sncf-regularite-tgv.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    par_annee: dict[int, dict[int, float]] = {}

    for ligne in _lignes():
        if ligne["regularite_composite"] is None:
            continue
        date = ligne["date"]
        par_annee.setdefault(date.year, {})[date.month] = float(ligne["regularite_composite"])

    resultat: list[dict] = []
    for annee, mois_valeurs in par_annee.items():
        if len(mois_valeurs) != 12:
            continue
        moyenne = sum(mois_valeurs.values()) / 12
        resultat.append(
            {"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": arrondi(moyenne, 2)}
        )

    return resultat


if __name__ == "__main__":
    for r in calculer():
        print(r)
