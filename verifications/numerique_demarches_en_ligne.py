"""Recalcul indépendant de numerique.demarches_en_ligne.

Source dinum-observatoire-demarches, une ligne par démarche et par édition. Valeur = 100 * nombre de lignes
où en_ligne == « Oui » / nombre total de lignes de l'édition, arrondie à 0,1. Période = periode (AAAA-MM) de
l'édition.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "dinum-observatoire-demarches.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select edition, periode, en_ligne from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    total: dict[str, int] = {}
    en_ligne: dict[str, int] = {}
    periode_de: dict[str, str] = {}
    for ligne in _lignes():
        edition = ligne["edition"]
        periode_de[edition] = ligne["periode"]
        total[edition] = total.get(edition, 0) + 1
        if ligne["en_ligne"] == "Oui":
            en_ligne[edition] = en_ligne.get(edition, 0) + 1

    resultat = []
    for edition, n in total.items():
        valeur = arrondi(100 * en_ligne.get(edition, 0) / n, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode_de[edition], "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer():
        print(r)
