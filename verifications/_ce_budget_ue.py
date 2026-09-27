"""Aide partagée : lecture des lignes agrégées du classeur « EU spending and revenue » normalisé."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ce-budget-ue-depenses-recettes.parquet"

LIBELLE_DEPENSES = "TOTAL EXPENDITURE"
LIBELLES_CONTRIBUTIONS = ("TOTAL national contribution", "TOTAL National contributions")
LIBELLE_RNB = "Gross National Income (GNI), EUR million"


def _valeurs(libelles) -> dict[tuple[str, int], float]:
    if isinstance(libelles, str):
        libelles = (libelles,)
    con = duckdb.connect()
    marqueurs = ", ".join(f"'{l}'" for l in libelles)
    lignes = con.execute(
        f"""
        select pays, annee, valeur
        from read_parquet('{FICHIER.as_posix()}')
        where libelle in ({marqueurs}) and valeur is not null
        """
    ).fetchall()
    return {(pays, annee): valeur for pays, annee, valeur in lignes}


def depenses() -> dict[tuple[str, int], float]:
    return _valeurs(LIBELLE_DEPENSES)


def contributions() -> dict[tuple[str, int], float]:
    return _valeurs(LIBELLES_CONTRIBUTIONS)


def rnb() -> dict[tuple[str, int], float]:
    return _valeurs(LIBELLE_RNB)
