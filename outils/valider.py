"""Validation du dépôt, lancée par la CI : catalogue, indicateurs et chiffrage des programmes.

    uv run python -m outils.valider
"""

from __future__ import annotations

import json
import sys

from jsonschema import Draft202012Validator

from pipelines.commun import RACINE, definitions_indicateurs, sources_du_catalogue



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

    from .chiffrage import valider as valider_chiffrage  # import tardif : chiffrage importe plan

    erreurs += valider_chiffrage()
    from .simulateur import valider as valider_simulateur

    erreurs += valider_simulateur()
    from .jeu import valider as valider_jeu

    erreurs += valider_jeu()
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
