"""Recalcul indépendant de culture.depense_publique_culture."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER_NUM = NORMALISE / "eurostat-gov-10a-exp-culture.parquet"
FICHIER_DEN = NORMALISE / "eurostat-nama-10-gdp-echanges.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    numerateur: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}
    for ligne in _lignes(FICHIER_NUM):
        if not (
            ligne["unit"].startswith("MIO_EUR")
            and ligne["sector"].startswith("S13")
            and ligne["cofog99"].partition(":")[0] == "GF0802"
            and ligne["na_item"].startswith("TE")
        ):
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, _, libelle = ligne["geo"].partition(":")
        numerateur[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

    denominateur: dict[tuple[str, str], float] = {}
    for ligne in _lignes(FICHIER_DEN):
        if not (ligne["unit"].startswith("CP_MEUR") and ligne["na_item"].startswith("B1GQ")):
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, _, _ = ligne["geo"].partition(":")
        denominateur[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    resultat: list[dict] = []
    for cle, num in numerateur.items():
        if cle not in denominateur:
            continue
        code, periode = cle
        valeur = arrondi(100 * num / denominateur[cle], 3)
        resultat.append({"maille": "pays", "code": code, "libelle": libelles[code], "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append(
                {"maille": "france", "code": "FR", "libelle": libelles[code], "periode": periode, "valeur": valeur}
            )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
