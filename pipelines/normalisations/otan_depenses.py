"""OTAN, « Defence expenditure of NATO countries » : classeur XLSX, un onglet par tableau (Table 1 à 8b).

Chaque onglet empile un ou plusieurs blocs : lignes de titre, une ligne d'années (2014 … « 2026e »), puis une
ligne par pays ou agrégat, jusqu'à une ligne vide. Le libellé du bloc est la dernière ligne de texte seul lue
avant la ligne d'années (« Share of real GDP (%) », « Annual real change (%) », « Equipment (a) »…).

Sortie longue : tableau, titre, bloc, pays, annee, estimation, valeur.
- pays : libellé de la première colonne, sans l'astérisque de renvoi ni la monnaie entre parenthèses.
- estimation : vrai si l'année porte le suffixe « e » (estimations de l'OTAN).
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import openpyxl

ANNEE = re.compile(r"^(\d{4})(e?)$")


def _annee(cellule) -> tuple[int, bool] | None:
    if (m := ANNEE.match(str(cellule).strip() if cellule is not None else "")):
        return int(m.group(1)), m.group(2) == "e"
    return None


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    classeurs = [f for f in fichiers if f.suffix == ".xlsx"]
    if len(classeurs) != 1:
        raise ValueError(f"{source['id']} : un classeur XLSX attendu, {len(classeurs)} trouvés")
    wb = openpyxl.load_workbook(classeurs[0], data_only=True, read_only=True)
    lignes_sortie = []
    for ws in wb.worksheets:
        lignes = list(ws.iter_rows(values_only=True))
        titre = str(lignes[0][0]).strip() if lignes and lignes[0][0] else ws.title
        bloc, annees = None, None
        for r in lignes[1:]:
            cellules = list(r)
            remplies = [c for c in cellules if c not in (None, "")]
            if not remplies:
                annees = None
                continue
            if cellules[0] in (None, "") and all(_annee(c) for c in remplies):
                annees = {i: _annee(c) for i, c in enumerate(cellules) if c not in (None, "")}
                continue
            if annees is None:
                if len(remplies) == 1 and isinstance(remplies[0], str):
                    bloc = remplies[0].strip()
                continue
            if not isinstance(cellules[0], str) or cellules[0].startswith("Notes"):
                annees = None
                continue
            pays = re.sub(r"\s*\(.*\)$", "", cellules[0].replace("*", "")).strip()
            for i, (annee, estimation) in annees.items():
                v = cellules[i] if i < len(cellules) else None
                if isinstance(v, (int, float)):
                    lignes_sortie.append((ws.title, titre, bloc, pays, annee, estimation, float(v)))
    if not lignes_sortie:
        raise ValueError(f"{source['id']} : aucune valeur lue")
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (tableau VARCHAR, titre VARCHAR, bloc VARCHAR, pays VARCHAR, annee INTEGER, "
        "estimation BOOLEAN, valeur DOUBLE)"
    )
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?, ?, ?)", lignes_sortie)
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")
