"""Lecture des fiches Markdown et des appels de chiffres {{ind:…}}."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from pipelines.commun import RACINE

# {{ind:sante.ald_sans_mt@1.0.0 | departement=23 | 2025}}  ou  {{ind:… | france | 2025}}
APPEL = re.compile(r"\{\{ind:([^}]+)\}\}")
# Un pourcentage, un montant ou un taux écrit en dur dans le corps d'une fiche
CHIFFRE_TAPE = re.compile(r"\d[\d  ]*(?:[,.]\d+)?\s?(?:%|‰|€|k€|M€|Md€|points?\b|pour (?:cent|mille|100 000))")


@dataclass(frozen=True)
class Appel:
    texte: str
    indicateur: str
    version: str
    maille: str
    code: str
    periode: str


def analyser_appel(texte: str, contenu: str) -> Appel:
    morceaux = [m.strip() for m in contenu.split("|")]
    if len(morceaux) != 3 or "@" not in morceaux[0]:
        raise ValueError(f"appel mal formé : {texte} (attendu {{{{ind:id@version | maille=code | période}}}})")
    indicateur, version = morceaux[0].split("@", 1)
    selecteur = morceaux[1]
    if selecteur == "france":
        maille, code = "france", "FR"
    elif "=" in selecteur:
        maille, code = (s.strip() for s in selecteur.split("=", 1))
    else:
        raise ValueError(f"sélecteur inconnu « {selecteur} » dans {texte}")
    return Appel(texte, indicateur, version, maille, code, morceaux[2])


def appels(corps: str) -> list[Appel]:
    return [analyser_appel(m.group(0), m.group(1)) for m in APPEL.finditer(corps)]


def chiffres_tapes(corps: str) -> list[str]:
    return CHIFFRE_TAPE.findall(APPEL.sub("", corps))


def lire_fiche(chemin: Path) -> tuple[dict, str]:
    texte = chemin.read_text(encoding="utf-8")
    if not texte.startswith("---\n"):
        raise ValueError(f"{chemin} : en-tête YAML manquant")
    _, entete, corps = texte.split("---\n", 2)
    return yaml.safe_load(entete), corps


def toutes_les_fiches() -> list[Path]:
    domaines = RACINE / "domaines"
    return sorted(
        p for p in domaines.rglob("*.md") if p.parent.name in {"diagnostic", "propositions"}
    )
