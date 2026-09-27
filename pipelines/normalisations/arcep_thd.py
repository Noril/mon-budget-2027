"""ARCEP, déploiements du haut et très haut débit fixe : un ZIP de shapefile par trimestre, maille commune.

Seule la table attributaire (DBF) est lue, sans dépendance géographique. Le trimestre est lu dans le nom
du fichier DBF (« communes_2026T2.dbf » -> 2026T2). Sortie longue :
trimestre, code_commune, commune, code_departement, locaux, ftth.
`locaux` = colonne Locaux (nombre de locaux de la commune), `ftth` = colonne ftth (locaux raccordables à la fibre).
Les libellés sont encodés en Latin-1 malgré le fichier .cpg (UTF-8) : ils sont décodés en Latin-1.
"""

from __future__ import annotations

import csv
import re
import struct
import tempfile
import zipfile
from pathlib import Path

import duckdb

TRIMESTRE = re.compile(r"(\d{4}T[1-4])", re.IGNORECASE)
CHAMPS = {"INSEE_COM": "code_commune", "NOM_COM": "commune", "INSEE_DEP": "code_departement", "Locaux": "locaux", "ftth": "ftth"}
COLONNES = ["trimestre", "code_commune", "commune", "code_departement", "locaux", "ftth"]


def _lire_dbf(contenu: bytes):
    nombre, entete, longueur = struct.unpack("<IHH", contenu[4:12])
    champs, position, pos = [], 32, 1
    while contenu[position] != 0x0D:
        d = contenu[position : position + 32]
        nom = d[:11].split(b"\0")[0].decode("latin-1")
        champs.append((nom, chr(d[11]), pos, d[16]))
        pos += d[16]
        position += 32
    for i in range(nombre):
        enreg = contenu[entete + i * longueur : entete + (i + 1) * longueur]
        if enreg[:1] == b"*":  # enregistrement supprimé
            continue
        ligne = {}
        for nom, type_, debut, taille in champs:
            if nom not in CHAMPS:
                continue
            brut = enreg[debut : debut + taille].decode("latin-1").strip()
            if type_ in "NF":
                ligne[CHAMPS[nom]] = float(brut) if brut and brut != "*" * len(brut) else None
            else:
                ligne[CHAMPS[nom]] = brut or None
        yield ligne


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", newline="", encoding="utf-8", delete=False) as tmp:
        ecrivain = csv.DictWriter(tmp, fieldnames=COLONNES)
        ecrivain.writeheader()
        for archive in fichiers:
            with zipfile.ZipFile(archive) as z:
                dbf = [n for n in z.namelist() if n.lower().endswith(".dbf")]
                if len(dbf) != 1:
                    raise ValueError(f"{archive.name} : {len(dbf)} fichiers DBF")
                if not (m := TRIMESTRE.search(Path(dbf[0]).name)):
                    raise ValueError(f"{archive.name} : trimestre introuvable dans {dbf[0]}")
                trimestre = m.group(1).upper()
                for ligne in _lire_dbf(z.read(dbf[0])):
                    ecrivain.writerow({"trimestre": trimestre, **ligne})
    types = {c: "VARCHAR" for c in COLONNES[:4]} | {"locaux": "DOUBLE", "ftth": "DOUBLE"}
    duckdb.sql(
        f"COPY (SELECT * FROM read_csv('{tmp.name}', header = true, columns = {types})) TO '{sortie}' (FORMAT parquet)"
    )
    Path(tmp.name).unlink()
