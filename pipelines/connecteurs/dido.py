"""Connecteur de l'API DiDo du SDES (données du ministère de la Transition écologique).

    acces:
      mode: dido
      url: https://data.statistiques.developpement-durable.gouv.fr/dido/api/v1/datafiles/<rid>
      parametres: {columns: "DEP_CODE,DPEENERGIE"}   # facultatif : colonnes et filtres (COLONNE: "eq:valeur")

Un fichier DiDo a plusieurs millésimes ; le dernier est souvent annoncé quelques jours avant sa
diffusion et renvoie alors une erreur 400. Le connecteur retient le millésime le plus récent déjà
diffusé (date_diffusion passée), lu dans la fiche du jeu de données, et le demande explicitement.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import httpx

DELAI = httpx.Timeout(30.0, read=900.0)


def _millesime(source: dict) -> dict:
    """Millésime le plus récent déjà diffusé : {millesime, date_diffusion, rows}."""
    url = source["acces"]["url"].rstrip("/")
    rid = url.rsplit("/", 1)[-1]
    fiche = httpx.get(url, timeout=DELAI, follow_redirects=True)
    fiche.raise_for_status()
    racine = url.split("/datafiles/")[0]
    jeu = httpx.get(f"{racine}/datasets/{fiche.json()['dataset']['id']}", timeout=DELAI, follow_redirects=True)
    jeu.raise_for_status()
    maintenant = datetime.now(timezone.utc)
    (fichier,) = [f for f in jeu.json()["datafiles"] if f["rid"] == rid]
    diffuses = [
        m for m in fichier["millesimes"] if datetime.fromisoformat(m["date_diffusion"].replace("Z", "+00:00")) <= maintenant
    ]
    if not diffuses:
        raise ValueError(f"{source['id']} : aucun millésime diffusé pour {rid}")
    return max(diffuses, key=lambda m: m["millesime"])


def metadonnees(source: dict) -> dict:
    m = _millesime(source)
    return {
        "titre": source["titre"],
        "licence": source["licence"],
        "millesime": m["millesime"],
        "lignes_annoncees": m.get("rows"),
        "modifie_le": datetime.fromisoformat(m["date_diffusion"].replace("Z", "+00:00")).isoformat(),
    }


def telecharger(source: dict, dossier: Path) -> list[tuple[str, Path]]:
    params = {"withColumnName": "true", "withColumnDescription": "false"}
    millesime = _millesime(source)["millesime"]
    params |= source["acces"].get("parametres", {}) | {"millesime": millesime}
    destination = dossier / f"donnees_{millesime}.csv"  # le millésime est relu par pipelines/normalisations/dido.py
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream(
        "GET", f"{source['acces']['url'].rstrip('/')}/csv", params=params, timeout=DELAI, follow_redirects=True
    ) as reponse:
        reponse.raise_for_status()
        url = str(reponse.url)
        with destination.open("wb") as f:
            for bloc in reponse.iter_bytes(1 << 20):
                f.write(bloc)
    return [(url, destination)]
