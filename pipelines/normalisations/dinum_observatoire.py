"""Observatoire de la qualité des démarches en ligne (DINUM) : un classeur ODS par édition trimestrielle.

Premier onglet, une ligne par démarche essentielle. Les intitulés de colonnes changent d'une édition à
l'autre (« Réalisable En Ligne » devient « Statut En ligne », casse et espaces finaux variables) : ils sont
reconnus par leur début, sans tenir compte de la casse. L'édition est lue dans le nom du fichier
(« observatoire-2-edition-13-avril-2026-.ods » -> edition 13, periode 2026-04). Sortie longue :
edition, periode, id_demarche, demarche, en_ligne, volumetrie_totale, volumetrie_en_ligne, satisfaction, handicap.
Les nombres sont lus dans l'attribut office:value des cellules numériques, sinon dans le texte
(virgule décimale) ; « À venir », « Non applicable », « – » et vides donnent NULL.
"""

from __future__ import annotations

import csv
import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import duckdb

T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
P = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8,
        "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
EDITION = re.compile(r"edition-(\d+)-([a-z]+)-(\d{4})")
# colonne de sortie -> débuts possibles de l'intitulé (sans accents, en minuscules)
COLONNES_SOURCE = {
    "demarche": ("nom demarche",),
    "id_demarche": ("id demarche",),
    "en_ligne": ("statut en ligne", "realisable en ligne"),
    "volumetrie_totale": ("volumetrie totale",),
    "volumetrie_en_ligne": ("volumetrie en ligne",),
    "satisfaction": ("note satisfaction", "satisfaction usagers"),
    "handicap": ("prise en compte handicap",),
}
NUMERIQUES = {"volumetrie_totale", "volumetrie_en_ligne", "satisfaction"}
COLONNES = ["edition", "periode", *COLONNES_SOURCE]


def _simplifier(texte: str) -> str:
    return unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower().strip()


def _lignes_ods(chemin: Path):
    racine = ET.fromstring(zipfile.ZipFile(chemin).read("content.xml"))
    feuille = next(racine.iter(f"{T}table"))
    for ligne in feuille.iter(f"{T}table-row"):
        cellules = []
        for c in ligne.iter(f"{T}table-cell"):
            valeur = c.get(f"{O}value") if c.get(f"{O}value-type") in ("float", "percentage") else None
            texte = " ".join("".join(p.itertext()) for p in c.findall(P)).strip()
            cellules += [(valeur, texte)] * min(int(c.get(f"{T}number-columns-repeated", "1")), 64)
        yield cellules


def _nombre(valeur: str | None, texte: str) -> float | None:
    if valeur is not None:
        return float(valeur)
    t = texte.replace(" ", "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def _edition(chemin: Path) -> tuple[str, str]:
    if not (m := EDITION.search(_simplifier(chemin.name))):
        raise ValueError(f"{chemin.name} : édition introuvable dans le nom")
    return m.group(1), f"{m.group(3)}-{MOIS[m.group(2)]:02d}"


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.writer(tmp)
        ecrivain.writerow(COLONNES)
        for chemin in fichiers:
            edition, periode = _edition(chemin)
            lignes = _lignes_ods(chemin)
            entete = [_simplifier(t) for _, t in next(lignes)]
            indices = {}
            for col, debuts in COLONNES_SOURCE.items():
                trouves = [i for i, e in enumerate(entete) if e.startswith(debuts)]
                if not trouves:
                    raise ValueError(f"{chemin.name} : colonne « {debuts[0]} » introuvable")
                indices[col] = trouves[0]
            for cellules in lignes:
                if len(cellules) <= indices["demarche"] or not cellules[indices["demarche"]][1]:
                    continue
                valeurs = []
                for col, i in indices.items():
                    v, t = cellules[i] if i < len(cellules) else (None, "")
                    valeurs.append(_nombre(v, t) if col in NUMERIQUES else (t or None))
                ecrivain.writerow([edition, periode, *valeurs])
    types = {c: "VARCHAR" for c in COLONNES} | {c: "DOUBLE" for c in NUMERIQUES}
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, columns = {types})) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
