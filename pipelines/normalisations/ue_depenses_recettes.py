"""Commission européenne, « EU spending and revenue » : un onglet par année (2000 … 2024), montants en M€.

Chaque onglet contient plusieurs tableaux (dépenses par rubrique, NextGenerationEU à partir de 2021, recettes,
RNB), chacun sous une ligne d'en-tête qui porte les codes pays (BE, BG … FR … ; EL pour la Grèce, UK jusqu'en
2020 ; astérisques de renvoi retirés). La mise en page change avec les cadres financiers : libellé en colonne D jusqu'en 2020, en colonnes A-B
ensuite. Le libellé d'une ligne est donc la concaténation des cellules texte situées avant la première colonne
pays, et chaque valeur est rattachée au code pays de l'en-tête le plus proche au-dessus.

Sortie longue : annee, ligne (numéro dans l'onglet), libelle (espaces réduits, astérisques de renvoi retirés),
pays, valeur. Les colonnes d'agrégats (Total, earmarked, non-EU, EU-27…) ne sont pas reprises.
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import openpyxl

CODE_PAYS = re.compile(r"^[A-Z]{2}$")


def _libelle(cellules) -> str:
    texte = " ".join(str(c) for c in cellules if isinstance(c, str) and c.strip())
    return re.sub(r"\s+", " ", texte.replace("*", "")).strip()


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    if len(fichiers) != 1:
        raise ValueError(f"{source['id']} : un classeur attendu, {len(fichiers)} trouvés")
    # le fichier est servi sans extension (…/document/download/<id>_en) : openpyxl le lit par un flux
    with fichiers[0].open("rb") as flux:
        wb = openpyxl.load_workbook(flux, data_only=True, read_only=True)
        lignes_sortie = _lire(wb)
    if not lignes_sortie:
        raise ValueError(f"{source['id']} : aucune valeur lue")
    con =duckdb.connect()
    con.execute("CREATE TABLE t (annee INTEGER, ligne INTEGER, libelle VARCHAR, pays VARCHAR, valeur DOUBLE)")
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?)", lignes_sortie)
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")


def _lire(wb) -> list[tuple]:
    lignes_sortie = []
    for ws in wb.worksheets:
        if not re.fullmatch(r"\d{4}", ws.title.strip()):
            continue
        annee = int(ws.title)
        colonnes: dict[int, str] | None = None
        for n, r in enumerate(ws.iter_rows(values_only=True), start=1):
            cellules = list(r)
            # « LU* » en 2022 : astérisque de renvoi collé au code
            codes = {
                j: c.replace("*", "").strip()
                for j, c in enumerate(cellules)
                if isinstance(c, str) and CODE_PAYS.match(c.replace("*", "").strip())
            }
            if "FR" in codes.values():
                colonnes = codes
                continue
            if colonnes is None:
                continue
            libelle = _libelle(cellules[: min(colonnes)])
            if not libelle:
                continue
            for j, pays in colonnes.items():
                v = cellules[j] if j < len(cellules) else None
                if isinstance(v, (int, float)):
                    lignes_sortie.append((annee, n, libelle, pays, float(v)))
    return lignes_sortie
