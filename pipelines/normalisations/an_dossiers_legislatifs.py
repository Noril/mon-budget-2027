"""Dossiers législatifs de l'Assemblée nationale (ZIP de JSON, un par législature) -> lois promulguées.

Chaque ZIP contient json/dossierParlementaire/<uid>.json : un dossier, avec l'arbre de ses actes
(actesLegislatifs.acteLegislatif, imbriqués). Une loi promulguée est un acte codeActe = « PROM-PUB »
(dateActe = date de promulgation, codeLoi = « 2024-42 », titreLoi, infoJO). Un dossier peut porter
plusieurs lois (loi ordinaire et loi organique examinées ensemble) et figurer dans deux législatures.

Sortie : une ligne par acte PROM-PUB et par fichier, sans dédoublonnage (fait par les indicateurs, sur
code_loi). `date_premier_depot` : plus ancienne date des actes « *-DEPOT » du dossier (dépôt du texte
dans la première assemblée saisie). Dates tronquées au jour (AAAA-MM-JJ), sans correction.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import duckdb


def _actes(noeud, sortie: list[dict]) -> None:
    if isinstance(noeud, dict):
        if "codeActe" in noeud:
            sortie.append(noeud)
        for v in noeud.values():
            _actes(v, sortie)
    elif isinstance(noeud, list):
        for v in noeud:
            _actes(v, sortie)


def _jour(valeur: str | None) -> str | None:
    return valeur[:10] if valeur else None


def lire_zip(f: Path) -> list[tuple]:
    lignes = []
    with zipfile.ZipFile(f) as z:
        for nom in z.namelist():
            if "/dossierParlementaire/" not in nom or not nom.endswith(".json"):
                continue
            d = json.loads(z.read(nom))["dossierParlementaire"]
            actes: list[dict] = []
            _actes(d.get("actesLegislatifs"), actes)
            depots = [a["dateActe"][:10] for a in actes if a["codeActe"].endswith("-DEPOT") and a.get("dateActe")]
            for a in actes:
                if a["codeActe"] != "PROM-PUB":
                    continue
                jo = a.get("infoJO") or {}
                lignes.append((
                    d["uid"], d.get("legislature"), (d.get("procedureParlementaire") or {}).get("libelle"),
                    a.get("codeLoi"), a.get("titreLoi"), _jour(a.get("dateActe")), min(depots) if depots else None,
                    _jour(jo.get("dateJO")), jo.get("referenceNOR"), f.name,
                ))
    return lignes


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    lignes = [ligne for f in fichiers for ligne in lire_zip(f)]
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (uid_dossier VARCHAR, legislature VARCHAR, procedure VARCHAR, code_loi VARCHAR, "
        "titre_loi VARCHAR, date_promulgation VARCHAR, date_premier_depot VARCHAR, date_jo VARCHAR, nor VARCHAR, "
        "fichier VARCHAR)"
    )
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", lignes)
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")
    con.close()
