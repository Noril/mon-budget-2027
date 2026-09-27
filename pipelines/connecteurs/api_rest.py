"""Connecteur des API REST interrogées par une requête GET paramétrée (export filtré d'un portail…).

    acces:
      mode: api-rest
      url: https://open.urssaf.fr/api/explore/v2.1/catalog/datasets/<jeu>/exports/parquet
      parametres: {where: 'startswith(code_ape, "62")'}   # filtre côté serveur
      entetes: {Accept: ...}                                # facultatif

Le fichier est enregistré sous « donnees.<extension> », l'extension étant déduite du type de contenu
(parquet, csv, json, xlsx) pour que la normalisation par défaut s'applique. Pas de date de
modification fiable par requête : la détection des changements se fait sur l'empreinte du fichier.
"""

from __future__ import annotations

from pathlib import Path

import httpx

DELAI = httpx.Timeout(30.0, read=600.0)
EXTENSIONS = {
    "parquet": ".parquet",
    "csv": ".csv",
    "json": ".json",
    "spreadsheetml": ".xlsx",
}


def metadonnees(source: dict) -> dict:
    return {"titre": source["titre"], "licence": source["licence"], "modifie_le": None}


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    acces = source["acces"]
    dossier.mkdir(parents=True, exist_ok=True)
    provisoire = dossier / "donnees.tmp"
    with httpx.stream(
        "GET", acces["url"], params=acces.get("parametres"), headers=acces.get("entetes"),
        timeout=DELAI, follow_redirects=True,
    ) as reponse:
        reponse.raise_for_status()
        type_contenu = reponse.headers.get("content-type", "")
        extension = next((e for cle, e in EXTENSIONS.items() if cle in type_contenu), None)
        if extension is None:
            raise ValueError(f"{source['id']} : type de contenu {type_contenu!r} non reconnu")
        url = str(reponse.url)
        with provisoire.open("wb") as f:
            for bloc in reponse.iter_bytes(1 << 20):
                f.write(bloc)
    return [(url, provisoire.rename(dossier / f"donnees{extension}"))]
