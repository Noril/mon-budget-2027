"""Connecteur des fichiers publiés à une URL fixe (INSEE, data.gouv.fr…).

Les serveurs n'exposent souvent ni Last-Modified ni ETag : la détection des changements
se fait sur l'empreinte du fichier téléchargé (voir pipelines.ingest). Exception : pour les
fichiers Melodi (INSEE), la date de mise à jour du produit est lue dans le catalogue Melodi.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import httpx

DELAI = httpx.Timeout(30.0, read=600.0)


def telecharger_url(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=DELAI, follow_redirects=True) as reponse:
        reponse.raise_for_status()
        with destination.open("wb") as f:
            for bloc in reponse.iter_bytes(1 << 20):
                f.write(bloc)
    return destination


MELODI = re.compile(r"^https://api\.insee\.fr/melodi/file/([^/]+)/([^/?]+)")


def _modifie_melodi(url: str) -> str | None:
    """Date de mise à jour du produit Melodi, lue dans le catalogue (heure de Paris -> ISO avec fuseau)."""
    if not (m := MELODI.match(url)):
        return None
    reponse = httpx.get(f"https://api.insee.fr/melodi/catalog/{m.group(1)}", timeout=DELAI, follow_redirects=True)
    reponse.raise_for_status()
    for produit in reponse.json().get("product", []):
        if produit.get("id") == m.group(2) and produit.get("modified"):
            date = datetime.fromisoformat(produit["modified"][:19]).replace(tzinfo=ZoneInfo("Europe/Paris"))
            return date.isoformat()
    return None


def metadonnees(source: dict) -> dict:
    url = source["acces"]["urls"][0]
    reponse = httpx.head(url, timeout=DELAI, follow_redirects=True)
    return {
        "titre": source["titre"],
        "licence": source["licence"],
        "modifie_le": _modifie_melodi(url),
        "etag": reponse.headers.get("etag"),
        "last_modified": reponse.headers.get("last-modified"),
    }


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    return [
        (url, telecharger_url(url, dossier / (Path(urlparse(url).path).name or "donnees")))
        for url in source["acces"]["urls"]
    ]
