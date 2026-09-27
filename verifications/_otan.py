"""Correspondance des noms de pays anglais du classeur OTAN vers les codes Eurostat, construite de façon
indépendante (convention Eurostat : Grèce = EL, Royaume-Uni = UK ; codes ISO 3166 alpha-2 sinon)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "otan-depenses-defense.parquet"

CODE_PAYS = {
    "Albania": "AL",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Canada": "CA",
    "Croatia": "HR",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "EL",
    "Hungary": "HU",
    "Iceland": "IS",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Montenegro": "ME",
    "NATO Europe and Canada": "OTAN_EUR_CA",
    "NATO Total": "OTAN",
    "Netherlands": "NL",
    "North Macedonia": "MK",
    "Norway": "NO",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovak Republic": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE",
    "Türkiye": "TR",
    "United Kingdom": "UK",
    "United States": "US",
}


def lire_bloc(tableau: str, bloc: str) -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select pays, annee, valeur
        from read_parquet('{FICHIER.as_posix()}')
        where tableau = '{tableau}' and bloc = '{bloc}' and valeur is not null
        """
    ).fetchall()

    resultat: list[dict] = []
    for pays, annee, valeur in lignes:
        if pays not in CODE_PAYS:
            raise ValueError(f"pays non couvert par la table de correspondance : {pays!r}")
        resultat.append(
            {"maille": "pays", "code": CODE_PAYS[pays], "libelle": pays, "periode": str(annee), "valeur": float(valeur)}
        )

    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
