"""Recalcul indépendant de education.ips_colleges_dispersion, agrégation en Python (pas de GROUP BY)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import statistics

import duckdb

from pipelines.commun import NORMALISE
from verifications._cog_communes import departement_par_commune

FICHIER_IPS = NORMALISE / "depp-ips-colleges.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_ips() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select rentree_scolaire, code_insee_de_la_commune, ips
            from read_parquet('{FICHIER_IPS.as_posix()}') where ips is not null"""
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _libelles_departements() -> dict[str, str]:
    con = duckdb.connect()
    return dict(con.execute(f"select DEP, LIBELLE from read_parquet('{FICHIER_COG_DEP.as_posix()}')").fetchall())


def calculer() -> list[dict]:
    dep_par_commune = departement_par_commune()
    libelles = _libelles_departements()

    par_departement: dict[tuple[str, str], list[float]] = {}
    par_france: dict[str, list[float]] = {}

    for ligne in _lignes_ips():
        periode = ligne["rentree_scolaire"]
        departement = dep_par_commune.get(ligne["code_insee_de_la_commune"])
        if departement is None:
            continue  # commune absente du COG

        par_departement.setdefault((periode, departement), []).append(ligne["ips"])
        par_france.setdefault(periode, []).append(ligne["ips"])

    resultat: list[dict] = []
    for (periode, code), valeurs in par_departement.items():
        if len(valeurs) < 2:
            continue  # départements de moins de 2 collèges omis
        valeur = arrondi(statistics.stdev(valeurs), 1)
        resultat.append(
            {"maille": "departement", "code": code, "libelle": libelles.get(code, code), "periode": periode, "valeur": valeur}
        )
    for periode, valeurs in par_france.items():
        valeur = arrondi(statistics.stdev(valeurs), 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
