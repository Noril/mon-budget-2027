"""APL de la DREES : un classeur par profession, un onglet « APL <année> » par millésime.

Sortie longue : annee, code_commune, commune, apl, apl_65, apl_62, apl_60, pop_standardisee, pop_totale.
Les colonnes « 65, 62, 60 ans » restreignent l'offre aux médecins de cet âge ou moins.
"""

from __future__ import annotations

import csv
import re
import tempfile
from pathlib import Path

import duckdb
import openpyxl

ONGLET = re.compile(r"^APL (\d{4})$")
COLONNES = ["annee", "code_commune", "commune", "apl", "apl_65", "apl_62", "apl_60", "pop_standardisee", "pop_totale"]


def _lignes(classeur: Path):
    wb = openpyxl.load_workbook(classeur, read_only=True)
    for ws in wb.worksheets:
        if not (m := ONGLET.match(ws.title.strip())):
            continue
        annee, dans_donnees = m.group(1), False
        for r in ws.iter_rows(values_only=True):
            if not dans_donnees:
                dans_donnees = r[0] == "Code commune INSEE"
                continue
            if r[0] is None or not str(r[0]).strip()[:2].isalnum():
                continue  # ligne d'unités sous l'en-tête, lignes vides
            yield [annee, str(r[0]).strip(), r[1], *r[2:8]]


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.writer(tmp)
        ecrivain.writerow(COLONNES)
        for classeur in fichiers:
            ecrivain.writerows(_lignes(classeur))
    types = {c: "VARCHAR" for c in COLONNES[:3]} | {c: "DOUBLE" for c in COLONNES[3:]}
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, columns = {types})) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
