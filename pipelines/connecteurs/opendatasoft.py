"""Connecteur des portails Opendatasoft (DREES, ameli, CAF, URSSAF, OFGL, Éducation…).

Par défaut, télécharge l'export Parquet complet du jeu. Si `acces.pieces` est renseigné,
télécharge ces pièces jointes à la place (jeux DREES livrés en XLSX).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import httpx

from .fichier import telecharger_url

DELAI = httpx.Timeout(30.0, read=600.0)


def _base(source: dict) -> str:
    acces = source["acces"]
    return f"{acces['portail'].rstrip('/')}/api/explore/v2.1/catalog/datasets/{acces['jeu']}"


def metadonnees(source: dict) -> dict:
    reponse = httpx.get(_base(source), timeout=DELAI, follow_redirects=True)
    reponse.raise_for_status()
    meta = reponse.json()["metas"]["default"]
    # `modified` date parfois de la dernière retouche des métadonnées ; `data_processed` suit les données
    dates = [d for d in (meta.get("modified"), meta.get("data_processed")) if d]
    return {
        "titre": meta.get("title"),
        "licence": meta.get("license"),
        "modifie_le": max(dates, key=datetime.fromisoformat) if dates else None,
    }


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    pieces = source["acces"].get("pieces")
    if not pieces:
        url = f"{_base(source)}/exports/parquet"
        return [(url, telecharger_url(url, dossier / "donnees.parquet"))]
    return [
        (url, telecharger_url(url, dossier / re.sub(r"_(xlsx|xls|csv|zip|7z|pdf)$", r".\1", piece)))
        for piece in pieces
        for url in [f"{_base(source)}/attachments/{piece}"]
    ]
