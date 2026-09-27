"""Recalcul indépendant de education.eleves_colleges_defavorises, agrégation en Python (pas de GROUP BY)."""

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


def _quantile_continu(valeurs: list[float], p: float) -> float:
    """Quantile continu (interpolation linéaire), méthode PERCENTILE_CONT / numpy 'linear'."""
    ordonnees = sorted(valeurs)
    n = len(ordonnees)
    if n == 1:
        return ordonnees[0]
    position = p * (n - 1)
    indice_bas = int(position)
    fraction = position - indice_bas
    if indice_bas + 1 >= n:
        return ordonnees[-1]
    return ordonnees[indice_bas] + fraction * (ordonnees[indice_bas + 1] - ordonnees[indice_bas])


def calculer() -> list[dict]:
    dep_par_commune = departement_par_commune()
    effectifs = _effectifs()
    libelles = _libelles_departements()

    # Collèges retenus (COG valide), par rentrée, avec leur département et leur ips.
    par_rentree: dict[str, list[tuple[str, float]]] = {}
    for ligne in _lignes_ips():
        departement = dep_par_commune.get(ligne["code_insee_de_la_commune"])
        if departement is None:
            continue
        par_rentree.setdefault(ligne["rentree_scolaire"], []).append((ligne["uai"], departement, ligne["ips"]))

    resultat: list[dict] = []
    for periode, colleges in par_rentree.items():
        seuil = _quantile_continu([ips for _, _, ips in colleges], 0.25)
        annee_rentree = periode[:4]

        # (departement | "FR") -> [eleves_defavorises, eleves_total]
        agrege: dict[str, list[int]] = {}
        for uai, departement, ips in colleges:
            eleves = effectifs.get((uai, annee_rentree))
            if eleves is None:
                continue  # collège sans effectif ou à effectif nul
            defavorise = ips < seuil

            for cle in (departement, "FR"):
                agrege.setdefault(cle, [0, 0])
                agrege[cle][1] += eleves
                if defavorise:
                    agrege[cle][0] += eleves

        for cle, (eleves_def, eleves_tot) in agrege.items():
            valeur = arrondi(100 * eleves_def / eleves_tot, 1) if eleves_tot else 0.0
            if cle == "FR":
                resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
            else:
                resultat.append(
                    {"maille": "departement", "code": cle, "libelle": libelles.get(cle, cle), "periode": periode, "valeur": valeur}
                )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
