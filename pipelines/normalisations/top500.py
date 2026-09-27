"""TOP500 : un classeur par liste semestrielle (TOP500_AAAAMM.xlsx), un onglet, une ligne par supercalculateur.

La liste (AAAA-MM) est lue dans le nom du fichier. Sortie longue :
liste, rang, nom, site, pays, rmax_tflops, rpeak_tflops.
"""

from __future__ import annotations

import csv
import re
import tempfile
from pathlib import Path

import duckdb
import openpyxl

LISTE = re.compile(r"TOP500_(\d{4})(\d{2})")
EN_TETES = {"Rank": "rang", "Name": "nom", "Site": "site", "Country": "pays", "Rmax [TFlop/s]": "rmax_tflops", "Rpeak [TFlop/s]": "rpeak_tflops"}
COLONNES = ["liste", *EN_TETES.values()]


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.writer(tmp)
        ecrivain.writerow(COLONNES)
        for classeur in fichiers:
            if not (m := LISTE.search(classeur.name)):
                raise ValueError(f"{classeur.name} : liste introuvable dans le nom")
            liste = f"{m.group(1)}-{m.group(2)}"
            lignes = openpyxl.load_workbook(classeur, read_only=True).worksheets[0].iter_rows(values_only=True)
            entete = list(next(lignes))
            indices = [entete.index(e) for e in EN_TETES]
            for r in lignes:
                if r[indices[0]] is not None:
                    ecrivain.writerow([liste, *(r[i] for i in indices)])
    types = {"liste": "VARCHAR", "rang": "INTEGER", "nom": "VARCHAR", "site": "VARCHAR", "pays": "VARCHAR",
             "rmax_tflops": "DOUBLE", "rpeak_tflops": "DOUBLE"}
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, columns = {types})) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
