"""Recalcul indépendant de recherche.dird_pib à partir du Parquet normalisé Eurostat."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-rd-e-gerdtot.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')
            where sectperf = 'TOTAL:Tous les secteurs'
              and unit = 'PC_GDP:Pourcentage du produit intérieur brut (PIB)'"""
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        brut = ligne["OBS_VALUE"]
        if brut is None or str(brut).strip() == "":
            continue  # valeur vide
        valeur = float(brut)
        code, _, libelle = ligne["geo"].partition(":")
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
