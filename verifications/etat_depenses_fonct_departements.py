"""Dépenses de fonctionnement des départements par habitant, OFGL départements consolidés.

Champ agregat = 'Dépenses de fonctionnement', categ = DEPT (exclut Métropole de Lyon, catégorie ML, et Paris
depuis 2019, catégorie PARIS), montant non vide et ptot > 0. Valeur = somme(montant) / somme(ptot), arrondi
à 2 décimales. Maille departement : dep_code -> COG 2026, avec 67A réparti sur 67 et 68 selon le siren.
Maille France (code FR) : toutes les lignes DEPT sauf dep_code 75, une seule fois chacune.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "ofgl-departements-consolides.parquet"
COG_DEP = NORMALISE / "insee-cog-departements.parquet"

SIREN_67 = "226700011"
SIREN_68 = "226800019"


def _libelles_departements() -> dict[str, str]:
    con = duckdb.connect()
    return dict(con.execute(f"select DEP, LIBELLE from read_parquet('{COG_DEP.as_posix()}')").fetchall())


def _lignes() -> list[tuple]:
    con = duckdb.connect()
    return con.execute(
        f"""
        select dep_code, siren, extract(year from exer) as annee, montant, ptot
        from read_parquet('{FICHIER.as_posix()}')
        where agregat = 'Dépenses de fonctionnement' and categ = 'DEPT'
          and montant is not null and ptot is not null and ptot > 0
        """
    ).fetchall()


def _codes_depuis_dep_code(dep_code: str, siren: str) -> list[str]:
    if dep_code == "67A":
        if siren == SIREN_67:
            return ["67"]
        if siren == SIREN_68:
            return ["68"]
        return ["67", "68"]  # Collectivité européenne d'Alsace, depuis 2021
    return [dep_code]


def calculer() -> list[dict]:
    dep_libelles = _libelles_departements()

    par_dep: dict[tuple[str, int], list[tuple[float, int]]] = {}
    par_france: dict[int, list[tuple[float, int]]] = {}

    for dep_code, siren, annee, montant, ptot in _lignes():
        if dep_code != "75":
            par_france.setdefault(annee, []).append((montant, ptot))
        for code in _codes_depuis_dep_code(dep_code, siren):
            par_dep.setdefault((code, annee), []).append((montant, ptot))

    resultat: list[dict] = []
    for (code, annee), paires in par_dep.items():
        if code not in dep_libelles:
            continue
        valeur = arrondi(sum(m for m, _ in paires) / sum(p for _, p in paires), 2)
        resultat.append(
            {"maille": "departement", "code": code, "libelle": dep_libelles[code], "periode": str(annee), "valeur": valeur}
        )

    for annee, paires in par_france.items():
        valeur = arrondi(sum(m for m, _ in paires) / sum(p for _, p in paires), 2)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": valeur})

    return resultat
