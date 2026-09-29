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
    """Ligne publiée jusqu'en 2020 ; à partir de 2021, reconstitution selon la `construction` :
    TOTAL Own resources - Customs duties - Sugar levies + TOTAL Balances and adjustments."""
    resultat = _valeurs(LIBELLES_CONTRIBUTIONS)
    ressources = _valeurs("TOTAL Own resources")
    douane = _valeurs("Customs duties")
    sucre = _valeurs("Sugar levies")
    ajustements = _valeurs("TOTAL Balances and adjustments")
    for cle, valeur in ressources.items():
        if cle in douane and cle in sucre and cle in ajustements and cle not in resultat:
            resultat[cle] = valeur - douane[cle] - sucre[cle] + ajustements[cle]
    return resultat


def rnb() -> dict[tuple[str, int], float]:
    return _valeurs(LIBELLE_RNB)
