"""Connecteur des fichiers à URL fixe dont le nom ne se lit pas dans l'URL, ou se répète d'une URL à l'autre.

    acces:
      mode: fichiers-nommes
      urls:
        - https://webgate.ec.europa.eu/ebsm/api/public/odp/download?key=...   # URL opaque
        - https://data.assemblee-nationale.fr/.../16/.../Dossiers_Legislatifs.json.zip
        - https://data.assemblee-nationale.fr/.../17/.../Dossiers_Legislatifs.json.zip  # même nom

Comme le mode `fichier`, mais chaque fichier est enregistré sous « <rang>_<nom> » : rang de l'URL dans
acces.urls (01, 02…), nom lu dans l'en-tête Content-Disposition ou, à défaut, dans le chemin de l'URL
(caractères autres que lettres, chiffres, point, tiret remplacés par « _ »). Le rang garde l'ordre de
acces.urls et évite qu'un fichier en écrase un autre. Pas de date de modification fiable : la détection
des changements se fait sur l'empreinte des fichiers (voir pipelines.ingest).
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx

DELAI = httpx.Timeout(30.0, read=600.0)
DISPOSITION = re.compile(r"filename\*=UTF-8''([^;]+)|filename=\"?([^\";]+)\"?", re.IGNORECASE)


def nom_fichier(url: str, disposition: str | None) -> str:
    nom = ""
    if disposition and (m := DISPOSITION.search(disposition)):
        nom = unquote(m.group(1) or m.group(2) or "")
    nom = nom or Path(urlparse(url).path).name or "donnees"
    return re.sub(r"[^\w.-]+", "_", nom, flags=re.ASCII).strip("_")


def metadonnees(source: dict) -> dict:
    return {"titre": source["titre"], "licence": source["licence"], "modifie_le": None}


def telecharger(source: dict, dossier: Path, essais: int = 3) -> list[tuple[str, Path]]:
    dossier.mkdir(parents=True, exist_ok=True)
    resultats = []
    for rang, url in enumerate(source["acces"]["urls"], start=1):
        for essai in range(1, essais + 1):
            try:
                with httpx.stream("GET", url, timeout=DELAI, follow_redirects=True) as reponse:
                    reponse.raise_for_status()
                    destination = dossier / f"{rang:02d}_{nom_fichier(url, reponse.headers.get('content-disposition'))}"
                    with destination.open("wb") as f:
                        for bloc in reponse.iter_bytes(1 << 20):
                            f.write(bloc)
                break
            except httpx.TransportError:
                if essai == essais:
                    raise
        resultats.append((url, destination))
    return resultats
