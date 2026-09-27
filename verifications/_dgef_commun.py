"""Fonction commune aux vérifications immigration.premiers_titres_* (source dgef-premiers-titres-motif)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "dgef-premiers-titres-motif.parquet"


def calculer_titres_motif(motif_principal: str) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(
        f"""
        select annee_fichier, nb_titres
        from read_parquet('{FICHIER.as_posix()}')
        where motif_principal = '{motif_principal}' and sous_motif = 'TOTAL'
        """
    )
    cols = [d[0] for d in cur.description]
    lignes = [dict(zip(cols, r)) for r in cur.fetchall()]

    resultat = []
    for ligne in lignes:
        if ligne["nb_titres"] in (None, "nc"):
            continue
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": ligne["annee_fichier"],
                "valeur": float(ligne["nb_titres"]),
            }
        )
    return resultat
