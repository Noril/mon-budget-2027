"""Recalcul indépendant de finances.pib_nominal.

Jeu Melodi DD_CNA_AGREGATS (insee-pib) : PIB aux prix du marché (B1GQ), prix courants (V),
euros (XDC), niveau (N), COUNTERPART_AREA = W0. OBS_VALUE en millions d'euros (UNIT_MULT = 6),
converti en milliards (/ 1000). Toutes les années publiées. Lignes identiques dédoublonnées.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "insee-pib.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    vues: set[tuple] = set()
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        if ligne["STO"] != "B1GQ":
            continue
        if ligne["PRICES"] != "V":
            continue
        if ligne["UNIT_MEASURE"] != "XDC":
            continue
        if ligne["TRANSFORMATION"] != "N":
            continue
        if ligne["COUNTERPART_AREA"] != "W0":
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        annee = ligne["TIME_PERIOD"]
        valeur_millions = float(ligne["OBS_VALUE"])
        cle_dedoublonnage = (annee, valeur_millions, ligne["OBS_STATUS"])
        if cle_dedoublonnage in vues:
            continue
        vues.add(cle_dedoublonnage)

        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": annee,
                "valeur": valeur_millions / 1000.0,
            }
        )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: x["periode"])[:10]:
        print(r)
