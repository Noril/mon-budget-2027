"""Utilitaire partagé (vérifications seulement) : rattachement d'une commune à son département via le COG 2026.

Règle (cf. construction de education.ips_colleges) : COM et ARM portent directement DEP ; COMD et COMA héritent
du DEP de leur COMPARENT ; un code présent à la fois en COM et en COMD prend la ligne COM ; communes absentes du
COG (collectivités d'outre-mer) ne sont pas rattachées (retour None).
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_COMMUNES = NORMALISE / "insee-cog-communes.parquet"


def departement_par_commune() -> dict[str, str]:
    con = duckdb.connect()
    lignes = con.execute(
        f"select TYPECOM, COM, DEP, COMPARENT from read_parquet('{FICHIER_COMMUNES.as_posix()}')"
    ).fetchall()

    dep_de: dict[str, str] = {}
    heritages: list[tuple[str, str]] = []
    for typecom, com, dep, comparent in lignes:
        if typecom in ("COM", "ARM"):
            dep_de[com] = dep
        else:  # COMD, COMA
            heritages.append((com, comparent))

    for com, comparent in heritages:
        if com in dep_de:
            continue  # un code présent en COM et en COMD prend la ligne COM
        if comparent in dep_de:
            dep_de[com] = dep_de[comparent]

    return dep_de
