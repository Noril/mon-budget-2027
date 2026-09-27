"""Recalcul indépendant de energie.solde_exportateur_electricite à partir d'ODRÉ eco2mix-national.

ech_physiques est négatif quand la France exporte ; solde exportateur = -somme des mois / 1e6 (TWh).
"""

from __future__ import annotations

import calendar

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "odre-eco2mix-national.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    par_annee: dict[str, dict[int, float]] = {}

    for ligne in _lignes():
        if ligne["ech_physiques"] is None:
            continue
        annee = ligne["annee"]
        mois = int(ligne["mois"])
        puissance_mw = float(ligne["ech_physiques"])
        nb_jours = calendar.monthrange(int(annee), mois)[1]
        energie_mwh = puissance_mw * 24 * nb_jours
        par_annee.setdefault(annee, {})[mois] = energie_mwh

    resultat: list[dict] = []
    for annee, mois_valeurs in par_annee.items():
        if len(mois_valeurs) != 12:
            continue
        total_twh = -sum(mois_valeurs.values()) / 1_000_000
        resultat.append(
            {"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": arrondi(total_twh, 3)}
        )

    return resultat


if __name__ == "__main__":
    for r in calculer():
        print(r)
