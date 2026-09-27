"""Connecteur des portails Opendatasoft (DREES, ameli, CAF, URSSAF, OFGL, Éducation…).

Télécharge l'export Parquet complet d'un jeu et renvoie les métadonnées du producteur.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import httpx

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


def telecharger(source: dict, destination: Path) -> list[str]:
    """Écrit l'export Parquet dans `destination` et renvoie les URL appelées."""
    url = f"{_base(source)}/exports/parquet"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=DELAI, follow_redirects=True) as reponse:
        reponse.raise_for_status()
        with destination.open("wb") as f:
            for bloc in reponse.iter_bytes(1 << 20):
                f.write(bloc)
    return [url]
