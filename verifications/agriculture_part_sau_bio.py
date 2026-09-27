"""Recalcul indépendant de agriculture.part_sau_bio à partir d'Eurostat org_cropar."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-org-cropar.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _garde_geo(code: str) -> bool:
    return len(code) == 2 or code.startswith("EU")


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not (
            ligne["unit"].startswith("PC_UAA")
            and ligne["crops"].startswith("UAAXK0000")
            and ligne["agprdmet"].startswith("TOTAL")
        ):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")
        if not _garde_geo(code):
            continue

        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
