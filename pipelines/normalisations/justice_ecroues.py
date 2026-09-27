"""Statistique mensuelle des établissements et des personnes écrouées (ministère de la Justice, DGAP-SSER).

Un classeur XLSX par mois (situation au 1er du mois). Deux tableaux sont lus :
- « Tab2 » : évolution mensuelle sur 25 mois des personnes écrouées détenues, par catégorie pénale
  (colonnes Date, PR, CP, CO, Ecroués détenus) ;
- « Tab6 » : effectifs détenus et capacités à la date du fichier (lignes Métropole, Outre-Mer,
  Total France entière ; colonnes Capacité norme circulaire, Capacité opérationnelle, Ecroués détenus).

Sortie longue : date_fichier, tableau, date, niveau, mesure, valeur. `date_fichier` = dernière date de Tab2,
qui est aussi la date de Tab6. Les dates sont au format AAAA-MM-JJ.
"""

from __future__ import annotations

import csv
import tempfile
from datetime import date, datetime
from pathlib import Path

import duckdb
import openpyxl

COLONNES = ["date_fichier", "tableau", "date", "niveau", "mesure", "valeur", "fichier"]
MESURES_TAB2 = {"PR": "prevenus", "CP": "condamnes_prevenus", "CO": "condamnes", "Ecroués détenus": "detenus"}
MESURES_TAB6 = {
    "Capacité norme circulaire": "capacite_norme_circulaire",
    "Capacité opérationnelle": "capacite_operationnelle",
    "Ecroués détenus": "detenus",
}


def _date(v) -> str:
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return date.fromisoformat(str(v).strip()[:10]).isoformat()


def _tableau(ws, premiere: str):
    """En-tête (ligne dont la 1re cellule vaut `premiere`) puis lignes jusqu'à la première ligne vide."""
    entete = None
    for r in ws.iter_rows(values_only=True):
        if entete is None:
            if r and r[0] is not None and str(r[0]).strip() == premiere:
                entete = [str(c).strip() if c is not None else None for c in r]
            continue
        if r[0] is None:
            break
        yield dict(zip(entete, r))


def _lignes(classeur: Path):
    wb = openpyxl.load_workbook(classeur, data_only=True)
    tab2 = [l for l in _tableau(wb["Tab2"], "Date") if l.get("Ecroués détenus") is not None]
    if not tab2:
        raise ValueError(f"{classeur.name} : Tab2 vide")
    date_fichier = max(_date(l["Date"]) for l in tab2)
    for l in tab2:
        for colonne, mesure in MESURES_TAB2.items():
            if l.get(colonne) is not None:
                yield [date_fichier, "Tab2", _date(l["Date"]), "Total France entière", mesure, float(l[colonne]), classeur.name]
    for l in _tableau(wb["Tab6"], "Niveau"):
        for colonne, mesure in MESURES_TAB6.items():
            if isinstance(l.get(colonne), (int, float)):
                yield [date_fichier, "Tab6", date_fichier, str(l["Niveau"]).strip(), mesure, float(l[colonne]), classeur.name]


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.writer(tmp)
        ecrivain.writerow(COLONNES)
        for classeur in fichiers:
            ecrivain.writerows(_lignes(classeur))
    types = {c: "VARCHAR" for c in COLONNES} | {"valeur": "DOUBLE"}
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, columns = {types})) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
