"""Recalcul indépendant de finances.dette_publique.

Eurostat gov_10dd_edpt1, unit = MIO_NAC. Numérateur : sector S13, na_item GD (dette brute
consolidée). Dénominateur : sector S1, na_item B1GQ (PIB), même pays même année.
Valeur = 100 * GD / B1GQ, sans arrondi. Maille france = ligne geo FR recopiée avec le code FR
(donc aussi présente en maille pays).
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
    dette: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}
    pib: dict[tuple[str, str], float] = {}

    for ligne in _lignes_brutes():
        if ligne["unit"] != "MIO_NAC:Millions d'unités de monnaie nationale":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, libelle = _code_libelle(ligne["geo"])
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])

        if ligne["sector"] == "S13:Administrations publiques" and ligne["na_item"] == "GD:Dette brute consolidée du gouvernement":
            dette[(code, annee)] = valeur
            libelles[code] = libelle
        elif ligne["sector"] == "S1:Economie totale" and ligne["na_item"] == "B1GQ:Produit intérieur brut aux prix du marché":
            pib[(code, annee)] = valeur

    resultat: list[dict] = []
    for (code, annee), num in dette.items():
        if (code, annee) not in pib:
            continue
        valeur = 100.0 * num / pib[(code, annee)]
        resultat.append({"maille": "pays", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
