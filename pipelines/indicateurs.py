"""Calcul des indicateurs : SQL DuckDB sur la zone normalisée -> table versionnée + lignage.

    uv run python -m pipelines.indicateurs
"""

from __future__ import annotations

import re
import sys

import duckdb

from .commun import (
    INDICATEURS_CALCULES,
    NORMALISE,
    RACINE,
    ControleEchoue,
    definitions_indicateurs,
    ecrire_json,
    lire_json,
    maintenant,
    sha256,
)

COLONNES = ["maille", "code", "libelle", "periode", "valeur"]
APPEL_SOURCE = re.compile(r"\{\{source:([a-z0-9-]+)\}\}")


def calculer(definition: dict) -> dict:
    chemin_sql = RACINE / definition["formule"]
    sql = chemin_sql.read_text(encoding="utf-8")

    appelees = set(APPEL_SOURCE.findall(sql))
    if appelees != set(definition["sources"]):
        raise ControleEchoue(f"{definition['id']} : sources du SQL {sorted(appelees)} ≠ sources déclarées")
    for s in appelees:
        if not (NORMALISE / f"{s}.parquet").exists():
            raise ControleEchoue(f"{definition['id']} : source {s} absente de la zone normalisée (lancer l'ingestion)")
    requete = APPEL_SOURCE.sub(lambda m: f"read_parquet('{NORMALISE / (m.group(1) + '.parquet')}')", sql)

    resultat = duckdb.sql(requete)
    if resultat.columns != COLONNES:
        raise ControleEchoue(f"{definition['id']} : colonnes {resultat.columns}, attendu {COLONNES}")

    mailles = {m for (m,) in duckdb.sql("SELECT DISTINCT maille FROM resultat").fetchall()}
    if not mailles <= set(definition["maille"]):
        raise ControleEchoue(f"{definition['id']} : mailles {sorted(mailles)} hors déclaration")
    doublons = duckdb.sql(
        "SELECT count(*) FROM (SELECT maille, code, periode FROM resultat GROUP BY ALL HAVING count(*) > 1)"
    ).fetchone()[0]
    if doublons:
        raise ControleEchoue(f"{definition['id']} : {doublons} doublons (maille, code, periode)")

    INDICATEURS_CALCULES.mkdir(parents=True, exist_ok=True)
    nom = f"{definition['id']}@{definition['version']}"
    sortie = INDICATEURS_CALCULES / f"{nom}.parquet"
    resultat.write_parquet(str(sortie))

    lignage = {
        "indicateur": definition["id"],
        "version": definition["version"],
        "calcule_le": maintenant(),
        "formule": definition["formule"],
        "formule_sha256": sha256(chemin_sql),
        "lignes": duckdb.sql(f"SELECT count(*) FROM read_parquet('{sortie}')").fetchone()[0],
        "sources": {s: lire_json(NORMALISE / f"{s}.manifeste.json") for s in sorted(appelees)},
    }
    ecrire_json(INDICATEURS_CALCULES / f"{nom}.lignage.json", lignage)
    print(f"  + {nom} : {lignage['lignes']} valeurs")
    return lignage


def main() -> int:
    echecs = []
    for _, definition in definitions_indicateurs():
        try:
            calculer(definition)
        except ControleEchoue as e:
            echecs.append(str(e))
    for e in echecs:
        print(f"ÉCHEC {e}", file=sys.stderr)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
