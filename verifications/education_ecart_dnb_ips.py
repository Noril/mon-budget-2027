"""Recalcul indépendant de education.ecart_dnb_ips, agrégation en Python (pas de GROUP BY)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE
from verifications._cog_communes import departement_par_commune

FICHIER_IPS = NORMALISE / "depp-ips-colleges.parquet"
FICHIER_VA = NORMALISE / "depp-va-colleges.parquet"


def _lignes_ips() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select rentree_scolaire, code_insee_de_la_commune, uai, ips
            from read_parquet('{FICHIER_IPS.as_posix()}') where ips is not null"""
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _va() -> dict[tuple[str, str], tuple[int, float]]:
    """(uai, session) -> (nb_candidats_g, taux_de_reussite_g)."""
    con = duckdb.connect()
    lignes = con.execute(
        f"""select uai, session, nb_candidats_g, taux_de_reussite_g from read_parquet('{FICHIER_VA.as_posix()}')
            where nb_candidats_g > 0 and taux_de_reussite_g is not null"""
    ).fetchall()
    return {(uai, str(session.year)): (candidats, taux) for uai, session, candidats, taux in lignes}


def _quantile_continu(valeurs: list[float], p: float) -> float:
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
    va = _va()

    # session -> [(uai, ips), ...] pour les collèges retenus (COG valide)
    par_session: dict[str, list[tuple[str, float]]] = {}
    for ligne in _lignes_ips():
        if dep_par_commune.get(ligne["code_insee_de_la_commune"]) is None:
            continue  # commune absente du COG
        annee_rentree = int(ligne["rentree_scolaire"][:4])
        session = str(annee_rentree + 1)
        par_session.setdefault(session, []).append((ligne["uai"], ligne["ips"]))

    resultat: list[dict] = []
    for session, colleges in par_session.items():
        toutes_ips = [ips for _, ips in colleges]
        q1 = _quantile_continu(toutes_ips, 0.25)
        q3 = _quantile_continu(toutes_ips, 0.75)

        somme_defavorise = [0, 0.0]  # [candidats, candidats*taux]
        somme_favorise = [0, 0.0]

        for uai, ips in colleges:
            if not (ips < q1 or ips > q3):
                continue
            brevet = va.get((uai, session))
            if brevet is None:
                continue
            candidats, taux = brevet
            cible = somme_defavorise if ips < q1 else somme_favorise
            cible[0] += candidats
            cible[1] += candidats * taux

        if somme_defavorise[0] == 0 or somme_favorise[0] == 0:
            continue

        taux_defavorise = somme_defavorise[1] / somme_defavorise[0]
        taux_favorise = somme_favorise[1] / somme_favorise[0]
        valeur = arrondi(taux_favorise - taux_defavorise, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": session, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer():
        print(r)
