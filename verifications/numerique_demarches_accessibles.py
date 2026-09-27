"""Recalcul indépendant de numerique.demarches_accessibles.

Source dinum-observatoire-demarches, lignes où en_ligne == « Oui ». Valeur = 100 * nombre de ces lignes dont
handicap == « Totale » / nombre de ces lignes, par édition, arrondie à 0,1.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "dinum-observatoire-demarches.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select edition, periode, en_ligne, handicap from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    total: dict[str, int] = {}
    totale: dict[str, int] = {}
    periode_de: dict[str, str] = {}
    for ligne in _lignes():
        if ligne["en_ligne"] != "Oui":
            continue
        edition = ligne["edition"]
        periode_de[edition] = ligne["periode"]
        total[edition] = total.get(edition, 0) + 1
        if ligne["handicap"] == "Totale":
            totale[edition] = totale.get(edition, 0) + 1

    resultat = []
    for edition, n in total.items():
        valeur = arrondi(100 * totale.get(edition, 0) / n, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode_de[edition], "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer():
        print(r)
