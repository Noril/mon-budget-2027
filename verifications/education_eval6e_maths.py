"""Recalcul indépendant de education.eval6e_maths, ligne à ligne en Python."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "depp-evaluations-6e-departements.parquet"

DISCIPLINE = "Mathématiques"
CARACTERISTIQUE = "Ensemble"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select * from read_parquet('{FICHIER.as_posix()}')
            where discipline = ? and caracteristique = ?""",
        [DISCIPLINE, CARACTERISTIQUE],
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        if ligne["groupe_1"] is None or ligne["groupe_2"] is None:
            continue
        valeur = arrondi(ligne["groupe_1"] + ligne["groupe_2"], 1)
        periode = str(ligne["annee"].year)

        if ligne["libelle_departement"] == "NATIONAL" and not ligne["code_departement"]:
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
        elif ligne["code_departement"]:
            resultat.append(
                {
                    "maille": "departement",
                    "code": ligne["code_departement"],
                    "libelle": ligne["libelle_departement"],
                    "periode": periode,
                    "valeur": valeur,
                }
            )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
