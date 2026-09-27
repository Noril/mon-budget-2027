"""Recalcul indépendant de education.reussite_dnb, agrégation en Python (pas de GROUP BY)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "depp-dnb-departements.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select session, dep_sco, presents, admis from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    # (periode, code) -> [somme_presents, somme_admis]
    departements: dict[tuple[str, str], list[int]] = {}
    france: dict[str, list[int]] = {}

    for ligne in _lignes_brutes():
        periode = str(ligne["session"].year)
        presents, admis = ligne["presents"] or 0, ligne["admis"] or 0

        cle_dep = (periode, ligne["dep_sco"])
        departements.setdefault(cle_dep, [0, 0])
        departements[cle_dep][0] += presents
        departements[cle_dep][1] += admis

        france.setdefault(periode, [0, 0])
        france[periode][0] += presents
        france[periode][1] += admis

    resultat: list[dict] = []
    for (periode, code), (somme_presents, somme_admis) in departements.items():
        if somme_presents == 0:
            continue
        valeur = arrondi(100 * somme_admis / somme_presents, 1)
        resultat.append({"maille": "departement", "code": code, "libelle": code, "periode": periode, "valeur": valeur})

    for periode, (somme_presents, somme_admis) in france.items():
        if somme_presents == 0:
            continue
        valeur = arrondi(100 * somme_admis / somme_presents, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
