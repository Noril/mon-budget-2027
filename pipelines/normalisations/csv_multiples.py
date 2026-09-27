"""Un ou plusieurs CSV (un par millésime, par exemple) -> un seul Parquet, colonnes en texte.

Chaque fichier est lu en texte (séparateur détecté, BOM retiré), les colonnes sont réunies par nom et deux
colonnes sont ajoutées : `fichier` (nom du fichier brut) et `annee_fichier` (première année 19xx ou 20xx lue
dans le nom du fichier, vide sinon). Accepte les fichiers sans extension (liens stables data.gouv.fr
/api/1/datasets/r/<ressource>, dont le nom local est l'identifiant de la ressource).
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb

ANNEE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    requetes = []
    for f in fichiers:
        annee = f"'{m.group(1)}'" if (m := ANNEE.search(f.name)) else "NULL::VARCHAR"
        requetes.append(
            f"SELECT *, '{f.name}' AS fichier, {annee} AS annee_fichier "
            f"FROM read_csv('{f}', all_varchar = true, header = true)"
        )
    duckdb.sql(f"COPY ({' UNION ALL BY NAME '.join(requetes)}) TO '{sortie}' (FORMAT parquet)")
