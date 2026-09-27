"""Recalcul indépendant de retraites.age_moyen_depart (CNAV, âge moyen à l'attribution, droits directs)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "cnav-age-attribution.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select annee, droits_directs from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        valeur = ligne["droits_directs"]
        if valeur is None:
            continue

        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France (régime général)",
                "periode": str(ligne["annee"].year),
                "valeur": float(valeur),
            }
        )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
