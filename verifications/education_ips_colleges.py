"""Recalcul indépendant de education.ips_colleges, agrégation en Python (pas de GROUP BY)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE
from verifications._cog_communes import departement_par_commune

FICHIER_IPS = NORMALISE / "depp-ips-colleges.parquet"
FICHIER_EFFECTIFS = NORMALISE / "depp-effectifs-colleges.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_ips() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select rentree_scolaire, code_insee_de_la_commune, uai, ips
            from read_parquet('{FICHIER_IPS.as_posix()}') where ips is not null"""
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _effectifs() -> dict[tuple[str, str], int]:
    """(numero_college, année de rentrée) -> nombre_eleves_total, effectifs nuls ou manquants exclus."""
    con = duckdb.connect()
    lignes = con.execute(
        f"""select numero_college, rentree_scolaire, nombre_eleves_total
            from read_parquet('{FICHIER_EFFECTIFS.as_posix()}')
            where nombre_eleves_total is not null and nombre_eleves_total > 0"""
    ).fetchall()
    return {(uai, str(rentree.year)): effectif for uai, rentree, effectif in lignes}


def _libelles_departements() -> dict[str, str]:
    con = duckdb.connect()
    return dict(con.execute(f"select DEP, LIBELLE from read_parquet('{FICHIER_COG_DEP.as_posix()}')").fetchall())


def calculer() -> list[dict]:
    dep_par_commune = departement_par_commune()
    effectifs = _effectifs()
    libelles = _libelles_departements()

    # periode -> departement|"FR" -> [somme(ips*eleves), somme(eleves)]
    par_departement: dict[tuple[str, str], list[float]] = {}
    par_france: dict[str, list[float]] = {}

    for ligne in _lignes_ips():
        periode = ligne["rentree_scolaire"]
        annee_rentree = periode[:4]

        eleves = effectifs.get((ligne["uai"], annee_rentree))
        if eleves is None:
            continue  # collège sans effectif ou à effectif nul

        departement = dep_par_commune.get(ligne["code_insee_de_la_commune"])
        if departement is None:
            continue  # commune absente du COG (collectivité d'outre-mer)

        cle_dep = (periode, departement)
        par_departement.setdefault(cle_dep, [0.0, 0])
        par_departement[cle_dep][0] += ligne["ips"] * eleves
        par_departement[cle_dep][1] += eleves

        par_france.setdefault(periode, [0.0, 0])
        par_france[periode][0] += ligne["ips"] * eleves
        par_france[periode][1] += eleves

    resultat: list[dict] = []
    for (periode, code), (somme_pondere, somme_eleves) in par_departement.items():
        valeur = arrondi(somme_pondere / somme_eleves, 1)
        resultat.append(
            {"maille": "departement", "code": code, "libelle": libelles.get(code, code), "periode": periode, "valeur": valeur}
        )
    for periode, (somme_pondere, somme_eleves) in par_france.items():
        valeur = arrondi(somme_pondere / somme_eleves, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
