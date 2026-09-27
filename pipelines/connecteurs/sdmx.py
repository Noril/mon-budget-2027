"""Connecteur SDMX 2.1 REST minimal, réponse en SDMX-CSV (Eurostat, FMI…).

    acces:
      mode: sdmx
      url: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/gov_10dd_edpt1
      cle: A.MIO_NAC.S13.B9+GD.        # clé de série : filtre côté serveur, évite les téléchargements énormes
      parametres: {format: SDMX-CSV}   # Eurostat : format demandé en paramètre
      entetes: {Accept: application/vnd.sdmx.data+csv}   # FMI : format demandé par en-tête

Les API SDMX n'exposent pas de date de modification fiable par requête : la détection des
changements se fait sur l'empreinte du fichier téléchargé (voir pipelines.ingest).
"""

from __future__ import annotations

from pathlib import Path

import httpx

DELAI = httpx.Timeout(30.0, read=600.0)


def url_requete(source: dict) -> str:
    acces = source["acces"]
    return f"{acces['url'].rstrip('/')}/{acces.get('cle', 'all')}"


def metadonnees(source: dict) -> dict:
    return {"titre": source["titre"], "licence": source["licence"], "modifie_le": None}


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    acces = source["acces"]
    destination = dossier / "donnees.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream(
        "GET",
        url_requete(source),
        params=acces.get("parametres"),
        headers=acces.get("entetes"),
        timeout=DELAI,
        follow_redirects=True,
    ) as reponse:
        reponse.raise_for_status()
        if "csv" not in reponse.headers.get("content-type", ""):
            raise ValueError(f"{source['id']} : réponse {reponse.headers.get('content-type')}, CSV attendu")
        url = str(reponse.url)
        with destination.open("wb") as f:
            for bloc in reponse.iter_bytes(1 << 20):
                f.write(bloc)
    return [(url, destination)]
