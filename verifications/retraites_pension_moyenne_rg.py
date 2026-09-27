"""Recalcul indépendant de retraites.pension_moyenne_rg (CNAV, montant global droit propre)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "cnav-pension-moyenne.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select categorie, montant_mensuel_moyen_de_la_retraite_globale_en_euros, annees_normees "
        f"from read_parquet('{FICHIER.as_posix()}')"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if ligne["categorie"] != "Droit propre":
            continue
        montant = ligne["montant_mensuel_moyen_de_la_retraite_globale_en_euros"]
        if montant is None:
            continue

        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France (régime général)",
                "periode": str(ligne["annees_normees"].year),
                "valeur": float(montant),
            }
        )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
