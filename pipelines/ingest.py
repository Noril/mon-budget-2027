"""Ingestion : source -> zone brute (horodatée, immuable) -> zone normalisée (Parquet contrôlé).

    uv run python -m pipelines.ingest                 # toutes les sources actives
    uv run python -m pipelines.ingest ameli-ald-sans-mt
    uv run python -m pipelines.ingest --force ...     # retélécharge même si le producteur n'a rien changé
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

import duckdb

from .commun import (
    BRUT,
    NORMALISE,
    ControleEchoue,
    charger_catalogue,
    commit_courant,
    ecrire_json,
    lire_json,
    maintenant,
    sha256,
)
from .connecteurs import CONNECTEURS


def dernier_manifeste(id_source: str) -> dict | None:
    dossiers = sorted((BRUT / id_source).glob("*/manifeste.json"))
    return lire_json(dossiers[-1]) if dossiers else None


def ingerer(source: dict, force: bool = False) -> dict:
    connecteur = CONNECTEURS[source["acces"]["mode"]]
    meta = connecteur.metadonnees(source)

    precedent = dernier_manifeste(source["id"])
    if precedent and not force and precedent["producteur"].get("modifie_le") == meta["modifie_le"]:
        print(f"  = {source['id']} : inchangé chez le producteur ({meta['modifie_le']})")
        return precedent

    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dossier = BRUT / source["id"] / horodatage
    fichier = dossier / "donnees.parquet"
    urls = connecteur.telecharger(source, fichier)

    lignes = duckdb.sql(f"SELECT count(*) FROM read_parquet('{fichier}')").fetchone()[0]
    manifeste = {
        "source": source["id"],
        "recupere_le": maintenant(),
        "urls": urls,
        "producteur": meta,
        "fichier": str(fichier.relative_to(BRUT.parent.parent)),
        "sha256": sha256(fichier),
        "octets": fichier.stat().st_size,
        "lignes": lignes,
        "commit_connecteur": commit_courant(),
    }
    ecrire_json(dossier / "manifeste.json", manifeste)
    print(f"  + {source['id']} : {lignes} lignes, sha256 {manifeste['sha256'][:12]}")
    return manifeste


def controler(source: dict, manifeste: dict, precedent: dict | None) -> list[str]:
    """Renvoie les alertes non bloquantes ; lève ControleEchoue si un contrôle bloque."""
    alertes = []
    fichier = BRUT.parent.parent / manifeste["fichier"]
    controles = source.get("controles", {})

    colonnes = {c[0] for c in duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{fichier}')").fetchall()}
    manquantes = set(controles.get("colonnes", [])) - colonnes
    if manquantes:
        raise ControleEchoue(f"{source['id']} : colonnes manquantes {sorted(manquantes)}")

    if manifeste["lignes"] < controles.get("lignes_min", 0):
        raise ControleEchoue(
            f"{source['id']} : {manifeste['lignes']} lignes, minimum attendu {controles['lignes_min']}"
        )

    if precedent and precedent["sha256"] != manifeste["sha256"] and precedent["lignes"]:
        ecart = abs(manifeste["lignes"] - precedent["lignes"]) / precedent["lignes"]
        if ecart > 0.2:
            raise ControleEchoue(f"{source['id']} : volumétrie en écart de {ecart:.0%} avec l'ingestion précédente")

    modifie = manifeste["producteur"].get("modifie_le")
    if modifie and "fraicheur_max_jours" in source:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(modifie)).days
        if age > source["fraicheur_max_jours"]:
            alertes.append(f"{source['id']} : dernière mise à jour du producteur il y a {age} jours")
    return alertes


def normaliser(source: dict, manifeste: dict) -> None:
    fichier = BRUT.parent.parent / manifeste["fichier"]
    NORMALISE.mkdir(parents=True, exist_ok=True)
    sortie = NORMALISE / f"{source['id']}.parquet"
    duckdb.sql(f"COPY (SELECT * FROM read_parquet('{fichier}')) TO '{sortie}' (FORMAT parquet)")
    ecrire_json(NORMALISE / f"{source['id']}.manifeste.json", manifeste)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sources", nargs="*", help="identifiants du catalogue (défaut : toutes les sources actives)")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    catalogue = charger_catalogue()
    ids = args.sources or [i for i, s in catalogue.items() if s.get("statut", "actif") == "actif"]
    echecs, alertes = [], []
    for id_source in ids:
        source = catalogue[id_source]
        if source.get("statut") == "a-brancher" or source["acces"]["mode"] not in CONNECTEURS:
            print(f"  ~ {id_source} : connecteur « {source['acces']['mode']} » pas encore branché")
            continue
        precedent = dernier_manifeste(id_source)
        try:
            manifeste = ingerer(source, force=args.force)
            alertes += controler(source, manifeste, precedent)
            normaliser(source, manifeste)
        except ControleEchoue as e:
            echecs.append(str(e))

    for a in alertes:
        print(f"ALERTE {a}")
    for e in echecs:
        print(f"ÉCHEC {e}", file=sys.stderr)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
