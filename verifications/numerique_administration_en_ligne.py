"""Recalcul indépendant de numerique.administration_en_ligne.

Eurostat isoc_ciegi_ac : particuliers ayant interagi en ligne avec une administration (I_IUGOV1),
en % des particuliers (PC_IND, IND_TOTAL). Lecture ligne à ligne en Python, pas de GROUP BY.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-isoc-ciegi-ac.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select indic_is, unit, ind_type, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not ligne["indic_is"].startswith("I_IUGOV1:"):
            continue
        if not ligne["unit"].startswith("PC_IND:"):
            continue
        if not ligne["ind_type"].startswith("IND_TOTAL:"):
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue
        valeur = float(ligne["OBS_VALUE"])
        periode = ligne["TIME_PERIOD"]
        code, libelle = _code_libelle(ligne["geo"])
        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
