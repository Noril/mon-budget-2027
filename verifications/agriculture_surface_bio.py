"""Recalcul indépendant de agriculture.surface_bio (surfaces bio Agence Bio par département)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "agencebio-surfaces-departement.parquet"
FICHIER_COG = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _nombre(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def calculer() -> list[dict]:
    cog = {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG)}

    resultat: list[dict] = []
    totaux_france: dict[str, float] = {}

    for ligne in _lignes(FICHIER):
        surf = _nombre(ligne["surfbio"])
        if surf is None:
            continue  # "NC"
        periode = ligne["annee"]
        code_dep = ligne["codedepartement"]

        totaux_france[periode] = totaux_france.get(periode, 0.0) + surf

        libelle = cog.get(code_dep)
        if libelle is not None:
            resultat.append(
                {
                    "maille": "departement",
                    "code": code_dep,
                    "libelle": libelle,
                    "periode": periode,
                    "valeur": arrondi(surf, 2),
                }
            )

    for periode, total in totaux_france.items():
        resultat.append(
            {"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": arrondi(total, 2)}
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
