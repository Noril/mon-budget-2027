"""Recalcul indépendant de immigration.premieres_demandes_asile.

Maille France : ligne niveau = Total, telle quelle. Maille département : lignes
niveau = Département, jointes (dict Python, pas de JOIN SQL) au COG 2026 sur
code_departement = DEP ; les codes qui ne correspondent à aucun département du
COG (N/D, 9715 Saint-Martin, "20" Corse non éclatée, code manquant) sont donc
naturellement écartés de cette maille.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ofpra-demandes-departement.parquet"
FICHIER_COG = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _libelles_departements() -> dict[str, str]:
    return {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG)}


def calculer() -> list[dict]:
    libelles = _libelles_departements()
    resultat: list[dict] = []

    for ligne in _lignes(FICHIER):
        annee = ligne["annee_fichier"]
        valeur = float(ligne["premiere_demande"])

        if ligne["niveau"] == "Total":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": valeur})
        elif ligne["niveau"] == "Département":
            code = ligne["code_departement"]
            if code in libelles:
                resultat.append(
                    {"maille": "departement", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur}
                )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
