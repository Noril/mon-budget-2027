"""Validation du dépôt, lancée par la CI : catalogue, indicateurs, fiches et leurs liens.

    uv run python -m outils.valider
"""

from __future__ import annotations

import json
import sys

from jsonschema import Draft202012Validator

from pipelines.commun import RACINE, definitions_indicateurs, sources_du_catalogue

from .fiches import appels, chiffres_tapes, lire_fiche, toutes_les_fiches


def _schema(nom: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((RACINE / "schemas" / f"{nom}.schema.json").read_text(encoding="utf-8")))


def _erreurs_schema(validateur: Draft202012Validator, objet: dict, ou: str) -> list[str]:
    return [f"{ou} : {'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in validateur.iter_errors(objet)]


def valider() -> list[str]:
    erreurs: list[str] = []

    sources = sources_du_catalogue()
    ids_sources = [s.get("id") for _, s in sources]
    for doublon in sorted({i for i in ids_sources if ids_sources.count(i) > 1}):
        erreurs.append(f"catalogue : source « {doublon} » déclarée plusieurs fois")
    schema_source = _schema("source")
    connecteurs = {p.stem for p in (RACINE / "pipelines" / "connecteurs").glob("*.py")}
    for fichier, s in sources:
        ou = f"{fichier.relative_to(RACINE)}:{s.get('id')}"
        erreurs += _erreurs_schema(schema_source, s, ou)
        mode = s.get("acces", {}).get("mode")
        # même règle que pipelines.connecteurs.connecteur : « api-rest » -> api_rest.py
        if s.get("statut", "actif") == "actif" and (mode or "").replace("-", "_") not in connecteurs:
            erreurs.append(f"{ou} : source active sans connecteur pipelines/connecteurs/{mode}.py")

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
