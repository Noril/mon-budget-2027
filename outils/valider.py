"""Validation du dépôt, lancée par la CI : catalogue, indicateurs, fiches et leurs liens.

    uv run python -m outils.valider
"""

from __future__ import annotations

import json
import sys

import yaml
from jsonschema import Draft202012Validator

from pipelines.commun import CATALOGUE, RACINE, definitions_indicateurs

from .fiches import appels, chiffres_tapes, lire_fiche, toutes_les_fiches


def _schema(nom: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((RACINE / "schemas" / f"{nom}.schema.json").read_text(encoding="utf-8")))


def _erreurs_schema(validateur: Draft202012Validator, objet: dict, ou: str) -> list[str]:
    return [f"{ou} : {'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in validateur.iter_errors(objet)]


def valider() -> list[str]:
    erreurs: list[str] = []

    sources = yaml.safe_load(CATALOGUE.read_text(encoding="utf-8"))
    ids_sources = [s.get("id") for s in sources]
    if len(ids_sources) != len(set(ids_sources)):
        erreurs.append("catalogue : identifiants de source en double")
    schema_source = _schema("source")
    for s in sources:
        erreurs += _erreurs_schema(schema_source, s, f"catalogue:{s.get('id')}")

    schema_indicateur = _schema("indicateur")
    indicateurs = {}
    for chemin, d in definitions_indicateurs():
        ou = str(chemin.relative_to(RACINE))
        erreurs += _erreurs_schema(schema_indicateur, d, ou)
        indicateurs[d.get("id")] = d
        for s in d.get("sources", []):
            if s not in ids_sources:
                erreurs.append(f"{ou} : source inconnue du catalogue « {s} »")
        if d.get("formule") and not (RACINE / d["formule"]).exists():
            erreurs.append(f"{ou} : formule introuvable {d['formule']}")

    schema_evaluation = _schema("evaluation")
    ids_evaluations = set()
    for chemin in sorted((RACINE / "sources").glob("*.md")):
        ou = str(chemin.relative_to(RACINE))
        try:
            entete, _ = lire_fiche(chemin)
        except ValueError as e:
            erreurs.append(f"{ou} : {e}")
            continue
        erreurs += _erreurs_schema(schema_evaluation, entete, ou)
        if entete.get("id") != chemin.stem:
            erreurs.append(f"{ou} : l'id « {entete.get('id')} » doit être le nom du fichier")
        ids_evaluations.add(entete.get("id"))

    schema_fiche = _schema("fiche")
    ids_fiches = set()
    renvois: list[tuple[str, str, str]] = []  # (fiche, champ, id visé)
    for chemin in toutes_les_fiches():
        ou = str(chemin.relative_to(RACINE))
        try:
            entete, corps = lire_fiche(chemin)
            liste = appels(corps)
        except ValueError as e:
            erreurs.append(f"{ou} : {e}")
            continue
        erreurs += _erreurs_schema(schema_fiche, entete, ou)
        if entete.get("id") in ids_fiches:
            erreurs.append(f"{ou} : id de fiche en double « {entete.get('id')} »")
        ids_fiches.add(entete.get("id"))
        if entete.get("id") != chemin.stem:
            erreurs.append(f"{ou} : l'id « {entete.get('id')} » doit être le nom du fichier")
        for champ in ("constats", "preuves"):
            renvois += [(ou, champ, cible) for cible in entete.get(champ) or []]
        for chiffre in chiffres_tapes(corps):
            erreurs.append(f"{ou} : chiffre tapé à la main « {chiffre.strip()} », appeler un indicateur à la place")
        declares = set(entete.get("indicateurs") or [])
        for a in liste:
            if a.indicateur not in indicateurs:
                erreurs.append(f"{ou} : indicateur inconnu {a.indicateur}")
                continue
            d = indicateurs[a.indicateur]
            if a.indicateur not in declares:
                erreurs.append(f"{ou} : {a.indicateur} utilisé mais absent de l'en-tête « indicateurs »")
            if a.version != d["version"]:
                erreurs.append(f"{ou} : {a.texte} appelle la version {a.version}, la définition est en {d['version']}")
            if a.maille not in d["maille"]:
                erreurs.append(f"{ou} : maille « {a.maille} » non calculée pour {a.indicateur}")

    for ou, champ, cible in renvois:
        connus = ids_fiches if champ == "constats" else ids_evaluations
        if cible not in connus:
            erreurs.append(f"{ou} : {champ} renvoie à « {cible} », introuvable")
    return erreurs


def main() -> int:
    erreurs = valider()
    for e in erreurs:
        print(f"ERREUR {e}", file=sys.stderr)
    if not erreurs:
        print("Dépôt valide.")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
