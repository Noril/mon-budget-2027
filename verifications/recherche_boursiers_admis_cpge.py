"""Recalcul indépendant de recherche.boursiers_admis_cpge, agrégation en Python (pas de GROUP BY)."""

from __future__ import annotations

import duckdb

from verifications._arrondi import arrondi

from pipelines.commun import NORMALISE

FICHIER_PARCOURSUP = NORMALISE / "sies-parcoursup.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"


def _codes_cog() -> set[str]:
    con = duckdb.connect()
    return {r[0] for r in con.execute(f"select DEP from read_parquet('{FICHIER_COG_DEP.as_posix()}')").fetchall()}


def _libelles_cog() -> dict[str, str]:
    con = duckdb.connect()
    return dict(con.execute(f"select DEP, LIBELLE from read_parquet('{FICHIER_COG_DEP.as_posix()}')").fetchall())


def _lignes_cpge() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select session, dep, acc_brs, acc_neobac from read_parquet('{FICHIER_PARCOURSUP.as_posix()}') where fili = 'CPGE'"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    codes_cog = _codes_cog()
    libelles = _libelles_cog()

    departements: dict[tuple[str, str], list[int]] = {}
    france: dict[str, list[int]] = {}

    for ligne in _lignes_cpge():
        periode = ligne["session"]
        brs, neobac = ligne["acc_brs"] or 0, ligne["acc_neobac"] or 0

        france.setdefault(periode, [0, 0])
        france[periode][0] += brs
        france[periode][1] += neobac

        if ligne["dep"] in codes_cog:
            cle = (periode, ligne["dep"])
            departements.setdefault(cle, [0, 0])
            departements[cle][0] += brs
            departements[cle][1] += neobac

    resultat: list[dict] = []
    for (periode, code), (somme_brs, somme_neobac) in departements.items():
        if somme_neobac == 0:
            continue  # aucun néo-bachelier admis
        valeur = arrondi(100 * somme_brs / somme_neobac, 1)
        resultat.append(
            {"maille": "departement", "code": code, "libelle": libelles.get(code, code), "periode": periode, "valeur": valeur}
        )

    for periode, (somme_brs, somme_neobac) in france.items():
        if somme_neobac == 0:
            continue
        valeur = arrondi(100 * somme_brs / somme_neobac, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
