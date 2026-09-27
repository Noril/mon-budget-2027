"""Connecteur des fichiers publiés à une URL fixe (INSEE, data.gouv.fr…).

Les serveurs n'exposent souvent ni Last-Modified ni ETag : la détection des changements
se fait sur l'empreinte du fichier téléchargé (voir pipelines.ingest).
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

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


def metadonnees(source: dict) -> dict:
    reponse = httpx.head(source["acces"]["urls"][0], timeout=DELAI, follow_redirects=True)
    return {
        "titre": source["titre"],
        "licence": source["licence"],
        "modifie_le": None,
        "etag": reponse.headers.get("etag"),
        "last_modified": reponse.headers.get("last-modified"),
    }


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    return [
        (url, telecharger_url(url, dossier / (Path(urlparse(url).path).name or "donnees")))
        for url in source["acces"]["urls"]
    ]
