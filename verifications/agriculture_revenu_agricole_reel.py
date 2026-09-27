"""Recalcul indépendant de agriculture.revenu_agricole_reel à partir d'Eurostat aact_eaa06."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-aact-eaa06.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    # Contrairement à ef_m_farmang / org_cropar, ce jeu Eurostat ne contient aucune région NUTS :
    # tous les geo présents sont des pays ou des agrégats (EA, EA21, EU, EU27_2020...), la définition
    # ne prévoit donc pas de filtre supplémentaire sur geo.
    resultat: list[dict] = []
    for ligne in _lignes():
        if not (ligne["indic_agr"].startswith("IND_A") and ligne["unit"].startswith("I10")):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")

        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
