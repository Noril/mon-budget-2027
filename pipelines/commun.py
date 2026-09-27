"""Chemins, lecture du catalogue et utilitaires partagés par les pipelines."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "data"
BRUT = DONNEES / "brut"
NORMALISE = DONNEES / "normalise"
INDICATEURS_CALCULES = DONNEES / "indicateurs"
CATALOGUE = RACINE / "indicateurs" / "catalogue.yaml"


class ControleEchoue(Exception):
    """Un contrôle de qualité bloque la chaîne en aval."""


def charger_catalogue() -> dict[str, dict]:
    sources = yaml.safe_load(CATALOGUE.read_text(encoding="utf-8"))
    return {s["id"]: s for s in sources}


def definitions_indicateurs() -> list[tuple[Path, dict]]:
    return [
        (chemin, yaml.safe_load(chemin.read_text(encoding="utf-8")))
        for chemin in sorted((RACINE / "indicateurs").rglob("*.yaml"))
        if chemin != CATALOGUE
    ]


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def maintenant() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def commit_courant() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=RACINE, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def ecrire_json(chemin: Path, contenu: dict) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lire_json(chemin: Path) -> dict:
    return json.loads(chemin.read_text(encoding="utf-8"))
