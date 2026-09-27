"""Aide partagée : lecture d'un filtre simple sur eurostat-gov-10a-exp (ou -defense).

Ces indicateurs recopient une valeur Eurostat déjà exprimée dans la bonne unité (% du PIB, % du total,
millions d'euros...) : pas de calcul, juste un filtre et un renommage des colonnes geo/TIME_PERIOD.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE


def lire_gov10a(fichier: str, unit: str, cofog99: str, na_item: str) -> list[dict]:
    chemin = NORMALISE / f"{fichier}.parquet"
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select geo, TIME_PERIOD, OBS_VALUE
        from read_parquet('{chemin.as_posix()}')
        where starts_with(unit, '{unit}:')
          and starts_with(sector, 'S13:')
          and starts_with(cofog99, '{cofog99}:')
          and starts_with(na_item, '{na_item}:')
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    vues: set[tuple[str, str, str, float]] = set()
    resultat: list[dict] = []
    for geo, periode, obs_value in lignes:
        code, _, libelle = geo.partition(":")
        cle = (code, libelle, periode, float(obs_value))
        if cle in vues:
            continue  # lignes strictement identiques dédoublonnées
        vues.add(cle)
        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": float(obs_value)})

    # maille france = ligne geo FR recopiée avec le code FR
    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
