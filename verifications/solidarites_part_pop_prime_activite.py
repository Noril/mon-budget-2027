"""Recalcul indépendant de solidarites.part_pop_prime_activite.

Numérateur : personnes couvertes par la prime d'activité (CAF, décembre de chaque année).
Dénominateur : population municipale 2023 (populations de référence INSEE), fixe pour toutes les années.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_CAF = NORMALISE / "caf-allocataires-departement.parquet"
FICHIER_POP = NORMALISE / "insee-populations-reference.parquet"

CODES_SANS_POPULATION = {"976", "978", "99", "XX"}


def _lignes_caf() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select dtreffre, numdep, indnbp_ppa from read_parquet('{FICHIER_CAF.as_posix()}') "
        f"where month(dtreffre) = 12"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _populations() -> dict[str, float]:
    con = duckdb.connect()
    lignes = con.execute(
        f"select GEO, OBS_VALUE from read_parquet('{FICHIER_POP.as_posix()}') "
        f"where GEO_OBJECT = 'DEP' and POPREF_MEASURE = 'PMUN'"
    ).fetchall()
    return {geo: float(valeur) for geo, valeur in lignes if valeur is not None and valeur != ""}


def calculer() -> list[dict]:
    populations = _populations()

    couverts: dict[tuple[str, int], int] = {}
    for ligne in _lignes_caf():
        numdep = ligne["numdep"]
        if numdep in CODES_SANS_POPULATION or numdep not in populations:
            continue
        annee = ligne["dtreffre"].year
        cle = (numdep, annee)
        couverts[cle] = couverts.get(cle, 0) + (ligne["indnbp_ppa"] or 0)

    resultat: list[dict] = []
    totaux_annee: dict[int, list[float]] = {}
    for (numdep, annee), somme in couverts.items():
        population = populations[numdep]
        valeur = arrondi(100 * somme / population, 2)
        resultat.append({"maille": "departement", "code": numdep, "libelle": numdep, "periode": str(annee), "valeur": valeur})
        totaux_annee.setdefault(annee, [0.0, 0.0])
        totaux_annee[annee][0] += somme
        totaux_annee[annee][1] += population

    for annee, (somme_couverts, somme_pop) in totaux_annee.items():
        valeur = arrondi(100 * somme_couverts / somme_pop, 2)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France hors Mayotte", "periode": str(annee), "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
