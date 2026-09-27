"""Recalcul indépendant de finances.taux_apparent.

Eurostat gov_10dd_edpt1, unit = MIO_NAC, sector S13. Valeur(t) = 100 * D41PAY(t) / GD(t-1) même
pays. Pas de valeur pour la première année de la série ni quand un terme manque.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-gov-10dd-edpt1.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    interets: dict[tuple[str, int], float] = {}
    dette: dict[tuple[str, int], float] = {}
    libelles: dict[str, str] = {}

    for ligne in _lignes_brutes():
        if ligne["unit"] != "MIO_NAC:Millions d'unités de monnaie nationale":
            continue
        if ligne["sector"] != "S13:Administrations publiques":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, libelle = _code_libelle(ligne["geo"])
        annee = int(ligne["TIME_PERIOD"])
        valeur = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

        if ligne["na_item"] == "D41PAY:Intérêts, dépenses":
            interets[(code, annee)] = valeur
        elif ligne["na_item"] == "GD:Dette brute consolidée du gouvernement":
            dette[(code, annee)] = valeur

    resultat: list[dict] = []
    for (code, annee), num in interets.items():
        precedent = (code, annee - 1)
        if precedent not in dette:
            continue
        valeur = 100.0 * num / dette[precedent]
        resultat.append({"maille": "pays", "code": code, "libelle": libelles[code], "periode": str(annee), "valeur": valeur})
        if code == "FR":
            resultat.append(
                {"maille": "france", "code": code, "libelle": libelles[code], "periode": str(annee), "valeur": valeur}
            )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
