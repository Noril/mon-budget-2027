from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "armees-militaires-carriere-contrat.parquet"


def calculer() -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select annee, statut, etpt
        from read_parquet('{FICHIER.as_posix()}')
        where categorie = 'ensemble' and armee = 'Total (hors gendarmerie)'
        """
    ).fetchall()

    par_annee: dict[int, dict[str, float]] = {}
    for annee, statut, etpt in lignes:
        if etpt is None:
            continue
        par_annee.setdefault(annee, {})[statut] = etpt

    resultat: list[dict] = []
    for annee, valeurs in par_annee.items():
        if "carrière" not in valeurs or "contrat" not in valeurs:
            continue
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": str(annee),
                "valeur": valeurs["carrière"] + valeurs["contrat"],
            }
        )
    return resultat
