"""Recalcul indépendant de agriculture.solde_agroalimentaire à partir d'Eurostat ext_lt_intratrd."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-ext-lt-intratrd.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not (ligne["indic_et"].startswith("MIO_BAL_VAL") and ligne["sitc06"].startswith("SITC0_1")):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")
        partenaire = ligne["partner"].partition(":")[0]

        if code == "EU27_2020":
            if partenaire != "EXT_EU27_2020":
                continue
        else:
            if partenaire != "WORLD":
                continue

        valeur = float(ligne["OBS_VALUE"]) / 1000.0
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
