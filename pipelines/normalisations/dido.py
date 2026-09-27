"""Fichiers DiDo (SDES) : CSV séparé par des points-virgules, nommé donnees_<millésime>.csv par le connecteur.

Recopie les colonnes en texte et ajoute la colonne `millesime` (AAAA-MM), que le fichier lui-même ne porte
pas : c'est la seule date de référence des fichiers annuels comme le RPLS (parc au 1er janvier).
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb

NOM = re.compile(r"^donnees_(\d{4}-\d{2})\.csv$")


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    (f,) = fichiers
    if not (m := NOM.match(f.name)):
        raise ValueError(f"{source['id']} : nom de fichier inattendu {f.name}, attendu donnees_AAAA-MM.csv")
    duckdb.sql(
        f"COPY (SELECT *, '{m.group(1)}' AS millesime FROM read_csv('{f}', delim = ';', header = true, all_varchar = true)) "
        f"TO '{sortie}' (FORMAT parquet)"
    )
