"""Rattachement commune -> département/région par le COG (utilitaire commun aux vérifications).

Règle telle que décrite dans les définitions YAML : TYPECOM COM ou ARM porte DEP et REG directement ;
COMD et COMA héritent de leur COMPARENT ; un code présent à la fois en COM/ARM et en COMD/COMA prend la
ligne COM/ARM.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_COG_COMMUNES = NORMALISE / "insee-cog-communes.parquet"
FICHIER_COG_DEP = NORMALISE / "insee-cog-departements.parquet"
FICHIER_COG_REG = NORMALISE / "insee-cog-regions.parquet"


def _lignes(fichier, colonnes="*") -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select {colonnes} from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in curseur.description]
    return [dict(zip(cols, ligne)) for ligne in curseur.fetchall()]


def rattachement_communes() -> dict[str, tuple[str, str]]:
    lignes = _lignes(FICHIER_COG_COMMUNES, "TYPECOM, COM, DEP, REG, COMPARENT")
    rattache: dict[str, tuple[str, str]] = {}
    for l in lignes:
        if l["TYPECOM"] in ("COM", "ARM") and l["DEP"] is not None:
            rattache[l["COM"]] = (l["DEP"], l["REG"])
    for l in lignes:
        if l["TYPECOM"] in ("COMD", "COMA") and l["COM"] not in rattache:
            parent = rattache.get(l["COMPARENT"])
            if parent is not None:
                rattache[l["COM"]] = parent
    return rattache


def departements_cog() -> set[str]:
    return {l["DEP"] for l in _lignes(FICHIER_COG_DEP, "DEP")}


def libelles_dep() -> dict[str, str]:
    return {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG_DEP, "DEP, LIBELLE")}


def libelles_reg() -> dict[str, str]:
    return {l["REG"]: l["LIBELLE"] for l in _lignes(FICHIER_COG_REG, "REG, LIBELLE")}
