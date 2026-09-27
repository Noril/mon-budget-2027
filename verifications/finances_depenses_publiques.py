"""Recalcul indépendant de finances.depenses_publiques.

Eurostat gov_10a_main, unit = PC_GDP, sector = S13, na_item = TE, valeur OBS_VALUE telle que
publiée (déjà en % du PIB). Code pays = partie de geo avant « : ». Maille france = ligne geo FR
recopiée avec le code FR. Lignes identiques dédoublonnées.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-gov-10a-main.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    vues: set[tuple] = set()
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        if ligne["unit"] != "PC_GDP:Pourcentage du produit intérieur brut (PIB)":
            continue
        if ligne["sector"] != "S13:Administrations publiques":
            continue
        if ligne["na_item"] != "TE:Total des dépenses des administrations publiques":
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, libelle = _code_libelle(ligne["geo"])
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])

        cle = (code, annee, valeur)
        if cle in vues:
            continue
        vues.add(cle)

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": annee, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": code, "libelle": libelle, "periode": annee, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
