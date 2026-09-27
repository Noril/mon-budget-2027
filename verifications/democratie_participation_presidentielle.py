"""Recalcul indépendant de democratie.participation_presidentielle."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "interieur-presidentielle-departements.parquet"
FICHIER_COG = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    cog = {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG)}

    resultat: list[dict] = []
    par_annee: dict[str, tuple[float, float]] = {}

    for ligne in _lignes(FICHIER):
        if ligne["scrutin"] != "presidentielle" or ligne["tour"] != 1:
            continue
        annee = str(ligne["annee"])
        votants, inscrits = float(ligne["votants"]), float(ligne["inscrits"])

        v, i = par_annee.get(annee, (0.0, 0.0))
        par_annee[annee] = (v + votants, i + inscrits)

        code_dep = ligne["code_departement"]
        libelle = cog.get(code_dep)
        if libelle is not None:
            resultat.append(
                {
                    "maille": "departement",
                    "code": code_dep,
                    "libelle": libelle,
                    "periode": annee,
                    "valeur": arrondi(100 * votants / inscrits, 2),
                }
            )

    for annee, (v, i) in par_annee.items():
        resultat.append(
            {"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": arrondi(100 * v / i, 2)}
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
