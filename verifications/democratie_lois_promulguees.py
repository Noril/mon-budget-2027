"""Recalcul indépendant de democratie.lois_promulguees à partir de an-dossiers-legislatifs.

Une loi = un code_loi distinct (dédoublonnage des dossiers présents dans deux législatures),
hors lois autorisant un accord international. Années 2018 à l'année précédant la plus récente.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "an-dossiers-legislatifs.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    codes_loi_retenus: set[str] = set()

    for ligne in _lignes():
        code_loi = ligne["code_loi"]
        if not code_loi:
            continue
        titre = ligne["titre_loi"] or ""
        if titre.strip().lower().startswith("autorisant"):
            continue
        codes_loi_retenus.add(code_loi)

    comptage: dict[str, int] = {}
    for code_loi in codes_loi_retenus:
        annee = code_loi[:4]
        comptage[annee] = comptage.get(annee, 0) + 1

    annee_max = max(int(a) for a in comptage)
    resultat: list[dict] = []
    for annee, nb in comptage.items():
        if not (2018 <= int(annee) <= annee_max - 1):
            continue
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": float(nb)})

    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: x["periode"]):
        print(r)
