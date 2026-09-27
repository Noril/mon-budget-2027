"""Recalcul indépendant de travail.taux_chomage.

Maille france : jeu Melodi DD_EEC_SERIES (insee-eec-series), EEC_MEASURE=UNEMPRATE, SEX=_T,
AGE=_T, EMPSTA=2, et _T pour EMPFORM, PCS, EDUC, WKTIME, UNDEREMP, UNEMPDUR, COMPOHALO ;
OBS_VALUE vide exclu ; valeur telle quelle, code FR, libellé "France hors Mayotte".
Maille pays : Eurostat une_rt_a, age=Y15-74, unit=PC_ACT, sex=T ; valeur OBS_VALUE telle quelle ;
code = partie de geo avant « : », libellé = partie après.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def _calculer_france() -> list[dict]:
    resultat = []
    for ligne in _lignes_brutes(NORMALISE / "insee-eec-series.parquet"):
        if ligne["EEC_MEASURE"] != "UNEMPRATE":
            continue
        if ligne["SEX"] != "_T":
            continue
        if ligne["AGE"] != "_T":
            continue
        if ligne["EMPSTA"] != "2":
            continue
        if ligne["EMPFORM"] != "_T":
            continue
        if ligne["PCS"] != "_T":
            continue
        if ligne["EDUC"] != "_T":
            continue
        if ligne["WKTIME"] != "_T":
            continue
        if ligne["UNDEREMP"] != "_T":
            continue
        if ligne["UNEMPDUR"] != "_T":
            continue
        if ligne["COMPOHALO"] != "_T":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France hors Mayotte",
                "periode": ligne["TIME_PERIOD"],
                "valeur": float(ligne["OBS_VALUE"]),
            }
        )
    return resultat


def _calculer_pays() -> list[dict]:
    resultat = []
    for ligne in _lignes_brutes(NORMALISE / "eurostat-une-rt-a.parquet"):
        if not ligne["age"].startswith("Y15-74:"):
            continue
        if not ligne["unit"].startswith("PC_ACT:"):
            continue
        if ligne["sex"] != "T:Total":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, libelle = _code_libelle(ligne["geo"])
        resultat.append(
            {"maille": "pays", "code": code, "libelle": libelle, "periode": ligne["TIME_PERIOD"], "valeur": float(ligne["OBS_VALUE"])}
        )
    return resultat


def calculer() -> list[dict]:
    return _calculer_france() + _calculer_pays()


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
