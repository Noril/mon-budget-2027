"""Recalcul indépendant de democratie.confiance_gouvernement à partir de l'Eurobaromètre standard.

Classement de l'item par le texte anglais (item_en), comme décrit dans la définition, sans utiliser
la colonne "institution" déjà calculée par la normalisation.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "eurobarometre-standard-confiance.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _garde_pays(code: str) -> bool:
    return len(code) == 2 or code == "EU27_2020"


def _periode(fin_terrain) -> str:
    semestre = "S1" if fin_terrain.month <= 6 else "S2"
    return f"{fin_terrain.year}-{semestre}"


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if "Government" not in ligne["item_en"]:
            continue
        if ligne["confiance"] is None:
            continue
        code = ligne["pays"]
        if not _garde_pays(code):
            continue

        valeur = arrondi(100 * ligne["confiance"], 0)
        periode = _periode(ligne["fin_terrain"])

        resultat.append({"maille": "pays", "code": code, "libelle": code, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "FR", "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
