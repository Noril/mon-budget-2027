"""Statistiques DVF (data.gouv.fr) servies par l'API tabulaire : CSV sans extension de fichier.

Recopie telles quelles les colonnes en texte (codes géographiques avec leurs zéros), sans la colonne
technique __id de l'API.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    (f,) = fichiers
    duckdb.sql(
        f"COPY (SELECT * EXCLUDE (__id) FROM read_csv('{f}', delim = ',', header = true, all_varchar = true)) "
        f"TO '{sortie}' (FORMAT parquet)"
    )
