"""Banque de données macroéconomiques de l'INSEE : flux SDMX-ML 2.1 « structure-specific » -> table longue.

Une ligne par observation : attributs de la série (IDBANK, INDICATEUR, REF_AREA, FREQ, CORRECTION, TITLE_FR,
LAST_UPDATE…) puis ceux de l'observation (TIME_PERIOD, OBS_VALUE, OBS_STATUS…). Tout est gardé en texte.
"""

from __future__ import annotations

import csv
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import duckdb


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _observations(fichier: Path):
    serie: dict[str, str] = {}
    for evenement, elem in ET.iterparse(fichier, events=("start", "end")):
        nom = _local(elem.tag)
        if evenement == "start" and nom == "Series":
            serie = dict(elem.attrib)
        elif evenement == "end" and nom == "Obs":
            yield serie | dict(elem.attrib)
            elem.clear()
        elif evenement == "end" and nom == "Series":
            elem.clear()


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    lignes = [o for f in fichiers for o in _observations(f)]
    if not lignes:
        raise ValueError(f"{source['id']} : aucune observation SDMX dans {[f.name for f in fichiers]}")
    colonnes = list(dict.fromkeys(c for o in lignes for c in o))
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.DictWriter(tmp, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, all_varchar = true)) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
