"""Ingestion : source -> zone brute (horodatée, immuable) -> zone normalisée (Parquet contrôlé).

    uv run python -m pipelines.ingest                 # toutes les sources actives
    uv run python -m pipelines.ingest ameli-ald-sans-mt
    uv run python -m pipelines.ingest --force ...     # retélécharge même si le producteur n'a rien changé
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone

import duckdb

from .commun import (
    BRUT,
    NORMALISE,
    RACINE,
    ControleEchoue,
    charger_catalogue,
    commit_courant,
    ecrire_json,
    lire_json,
    maintenant,
    sha256,
)
from .connecteurs import connecteur as charger_connecteur
from .normalisations import normaliser


def dernier_manifeste(id_source: str) -> dict | None:
    for chemin in sorted((BRUT / id_source).glob("*/manifeste.json"), reverse=True):
        if "fichiers" in (m := lire_json(chemin)):  # ignore les manifestes d'avant le format multi-fichiers
            return m
    return None


def ingerer(source: dict, force: bool = False) -> dict:
    """Renvoie le manifeste de l'instantané brut à utiliser (nouveau ou précédent si rien n'a changé)."""
    connecteur = charger_connecteur(source["acces"]["mode"])
    meta = connecteur.metadonnees(source)
    precedent = dernier_manifeste(source["id"])
    if precedent and not force and meta.get("modifie_le") and precedent["producteur"].get("modifie_le") == meta["modifie_le"]:
        print(f"  = {source['id']} : inchangé chez le producteur ({meta['modifie_le']})")
        return precedent

    dossier = BRUT / source["id"] / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fichiers = [
        {"url": url, "fichier": str(f.relative_to(RACINE)), "sha256": sha256(f), "octets": f.stat().st_size}
        for url, f in connecteur.telecharger(source, dossier)
    ]
    if precedent and not force and [f["sha256"] for f in fichiers] == [f["sha256"] for f in precedent["fichiers"]]:
        shutil.rmtree(dossier)
        print(f"  = {source['id']} : fichiers identiques à l'instantané précédent")
        return precedent

    manifeste = {
        "source": source["id"],
        "recupere_le": maintenant(),
        "producteur": meta,
        "fichiers": fichiers,
        "commit_connecteur": commit_courant(),
    }
    ecrire_json(dossier / "manifeste.json", manifeste)
    print(f"  + {source['id']} : {len(fichiers)} fichier(s), {sum(f['octets'] for f in fichiers) // 1024} Ko")
    return manifeste


def controler(source: dict, lignes: int, colonnes: set[str], manifeste: dict, lignes_avant: int | None) -> list[str]:
    """Renvoie les alertes non bloquantes ; lève ControleEchoue si un contrôle bloque."""
    alertes = []
    controles = source.get("controles", {})
    if manquantes := set(controles.get("colonnes", [])) - colonnes:
        raise ControleEchoue(f"{source['id']} : colonnes manquantes {sorted(manquantes)}")
    if lignes < controles.get("lignes_min", 0):
        raise ControleEchoue(f"{source['id']} : {lignes} lignes, minimum attendu {controles['lignes_min']}")
    if lignes_avant and abs(lignes - lignes_avant) / lignes_avant > 0.2:
        raise ControleEchoue(f"{source['id']} : {lignes} lignes contre {lignes_avant} à l'ingestion précédente (écart > 20 %)")
    modifie = manifeste["producteur"].get("modifie_le")
    if modifie and "fraicheur_max_jours" in source:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(modifie)).days
        if age > source["fraicheur_max_jours"]:
            alertes.append(f"{source['id']} : dernière mise à jour du producteur il y a {age} jours")
    return alertes


def normaliser_et_controler(source: dict, manifeste: dict) -> list[str]:
    sortie = NORMALISE / f"{source['id']}.parquet"
    a_jour = NORMALISE / f"{source['id']}.manifeste.json"
    avant = lire_json(a_jour) if a_jour.exists() else None
    provisoire = sortie.with_suffix(".tmp.parquet")
    normaliser(source, [RACINE / f["fichier"] for f in manifeste["fichiers"]], provisoire)

    lignes = duckdb.sql(f"SELECT count(*) FROM read_parquet('{provisoire}')").fetchone()[0]
    colonnes = {c[0] for c in duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{provisoire}')").fetchall()}
    lignes_avant = avant["lignes"] if avant and avant["recupere_le"] != manifeste["recupere_le"] else None
    try:
        alertes = controler(source, lignes, colonnes, manifeste, lignes_avant)
    except ControleEchoue:
        provisoire.unlink()
        raise
    provisoire.replace(sortie)
    ecrire_json(a_jour, manifeste | {"lignes": lignes, "normalise": str(sortie.relative_to(RACINE))})
    print(f"    {source['id']} : {lignes} lignes normalisées")
    return alertes


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
        if source.get("statut") == "a-brancher" or charger_connecteur(source["acces"]["mode"]) is None:
            print(f"  ~ {id_source} : connecteur « {source['acces']['mode']} » pas encore branché")
            continue
        try:
            alertes += normaliser_et_controler(source, ingerer(source, force=args.force))
        except ControleEchoue as e:
            echecs.append(str(e))
        except Exception as e:  # une source cassée ne bloque pas les autres
            echecs.append(f"{id_source} : {type(e).__name__} : {e}")

    for a in alertes:
        print(f"ALERTE {a}")
    for e in echecs:
        print(f"ÉCHEC {e}", file=sys.stderr)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
