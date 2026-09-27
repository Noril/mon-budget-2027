"""Normalisation : fichiers bruts d'une source -> un Parquet unique dans la zone normalisée.

Sans module dédié (`normalisation` dans le catalogue), `par_defaut` gère les cas simples :
Parquet recopié, CSV lu en texte (les codes géographiques gardent leurs zéros), ZIP décompressé.
"""

from __future__ import annotations

import fnmatch
import importlib
import zipfile
from pathlib import Path

import duckdb


def _csv_en_parquet(csv: Path, sortie: Path) -> None:
    duckdb.sql(f"COPY (SELECT * FROM read_csv('{csv}', all_varchar = true)) TO '{sortie}' (FORMAT parquet)")


def par_defaut(source: dict, fichiers: list[Path], sortie: Path) -> None:
    motif = source["acces"].get("motif", "*")
    candidats: list[Path] = []
    for f in fichiers:
        if zipfile.is_zipfile(f):  # Melodi sert ses ZIP sans extension
            dossier = f.parent / f"{f.name}.d"
            with zipfile.ZipFile(f) as z:
                z.extractall(dossier)
            candidats += sorted(dossier.rglob("*"))
        else:
            candidats.append(f)
    retenus = [f for f in candidats if f.is_file() and fnmatch.fnmatch(f.name, motif)]
    if len(retenus) != 1:
        raise ValueError(f"{source['id']} : {len(retenus)} fichiers correspondent à « {motif} », préciser acces.motif")
    (f,) = retenus
    if f.suffix == ".parquet":
        duckdb.sql(f"COPY (SELECT * FROM read_parquet('{f}')) TO '{sortie}' (FORMAT parquet)")
    elif f.suffix == ".csv":
        _csv_en_parquet(f, sortie)
    else:
        raise ValueError(f"{source['id']} : format {f.suffix} sans normalisation dédiée")


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    sortie.parent.mkdir(parents=True, exist_ok=True)
    if module := source.get("normalisation"):
        importlib.import_module(f"pipelines.normalisations.{module}").normaliser(source, fichiers, sortie)
    else:
        par_defaut(source, fichiers, sortie)
