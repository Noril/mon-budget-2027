"""Taux d'épargne brute des départements, OFGL départements consolidés, categ = DEPT.

Par collectivité (dep_code, siren) et année : épargne = somme(montant) pour agregat = 'Epargne brute',
recettes = somme(montant) pour agregat = 'Recettes de fonctionnement' ; collectivités sans épargne ou
recettes nulles écartées. Valeur = 100 * somme(épargnes) / somme(recettes), arrondi à 2 décimales.
Maille departement : dep_code -> COG 2026, 67A réparti sur 67/68 selon siren. Maille France (FR) : toutes
les collectivités DEPT sauf dep_code 75, une seule fois chacune.
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
        select dep_code, siren, extract(year from exer) as annee, agregat, sum(montant) as total
        from read_parquet('{FICHIER.as_posix()}')
        where categ = 'DEPT' and agregat in ('Epargne brute', 'Recettes de fonctionnement') and montant is not null
        group by 1, 2, 3, 4
        """
    ).fetchall()


def _codes_depuis_dep_code(dep_code: str, siren: str) -> list[str]:
    if dep_code == "67A":
        if siren == SIREN_67:
            return ["67"]
        if siren == SIREN_68:
            return ["68"]
        return ["67", "68"]
    return [dep_code]


def calculer() -> list[dict]:
    dep_libelles = _libelles_departements()

    par_collectivite: dict[tuple[str, str, int], dict[str, float]] = {}
    for dep_code, siren, annee, agregat, total in _lignes():
        par_collectivite.setdefault((dep_code, siren, annee), {})[agregat] = total

    par_dep: dict[tuple[str, int], list[tuple[float, float]]] = {}
    par_france: dict[int, list[tuple[float, float]]] = {}

    for (dep_code, siren, annee), valeurs in par_collectivite.items():
        if "Epargne brute" not in valeurs:
            continue
        recettes = valeurs.get("Recettes de fonctionnement")
        if not recettes:
            continue
        paire = (valeurs["Epargne brute"], recettes)

        if dep_code != "75":
            par_france.setdefault(annee, []).append(paire)
        for code in _codes_depuis_dep_code(dep_code, siren):
            par_dep.setdefault((code, annee), []).append(paire)

    resultat: list[dict] = []
    for (code, annee), paires in par_dep.items():
        if code not in dep_libelles:
            continue
        valeur = arrondi(100 * sum(e for e, _ in paires) / sum(r for _, r in paires), 2)
        resultat.append(
            {"maille": "departement", "code": code, "libelle": dep_libelles[code], "periode": str(annee), "valeur": valeur}
        )

    for annee, paires in par_france.items():
        valeur = arrondi(100 * sum(e for e, _ in paires) / sum(r for _, r in paires), 2)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": valeur})

    return resultat
