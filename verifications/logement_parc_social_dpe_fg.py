"""Recalcul indépendant de logement.parc_social_dpe_fg.

Source sdes-rpls-logements, une ligne par logement social (DEP_CODE, DPEENERGIE, millesime). Période = 4
premiers caractères de millesime. Lignes retenues : DPEENERGIE dans {A,B,C,D,E,F,G} (vide/NULL exclu).
Valeur = 100 * nombre de lignes F ou G / nombre de lignes retenues, arrondie à 0,1, par département et pour
la France (toutes les lignes retenues).
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "sdes-rpls-logements.parquet"
ETIQUETTES_VALIDES = {"A", "B", "C", "D", "E", "F", "G"}
ETIQUETTES_FG = {"F", "G"}


def calculer() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select DEP_CODE, DPEENERGIE, millesime from read_parquet('{FICHIER.as_posix()}')")

    total_dep: dict[tuple[str, str], int] = {}
    fg_dep: dict[tuple[str, str], int] = {}
    total_france: dict[str, int] = {}
    fg_france: dict[str, int] = {}

    for dep_code, dpe, millesime in curseur.fetchall():
        if dpe not in ETIQUETTES_VALIDES:
            continue
        periode = millesime[:4]
        total_dep[(dep_code, periode)] = total_dep.get((dep_code, periode), 0) + 1
        total_france[periode] = total_france.get(periode, 0) + 1
        if dpe in ETIQUETTES_FG:
            fg_dep[(dep_code, periode)] = fg_dep.get((dep_code, periode), 0) + 1
            fg_france[periode] = fg_france.get(periode, 0) + 1

    resultat: list[dict] = []
    for (dep, periode), total in total_dep.items():
        valeur = arrondi(100 * fg_dep.get((dep, periode), 0) / total, 1)
        resultat.append({"maille": "departement", "code": dep, "libelle": dep, "periode": periode, "valeur": valeur})
    for periode, total in total_france.items():
        valeur = arrondi(100 * fg_france.get(periode, 0) / total, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France métropolitaine", "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
