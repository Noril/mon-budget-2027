"""Recalcul indépendant de economie.solde_biens.

Eurostat nama_10_gdp, unit = CP_MEUR. Pour chaque pays et année : exportations de biens
(P61), importations de biens (P71), PIB aux prix du marché (B1GQ). Valeur = 100 * (P61 - P71) /
B1GQ, arrondie à 2 décimales ; lignes où l'un des trois manque exclues. Maille france = ligne
geo FR recopiée avec le code FR.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-nama-10-gdp-echanges.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    exports: dict[tuple[str, str], float] = {}
    imports_: dict[tuple[str, str], float] = {}
    pib: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}

    for ligne in _lignes_brutes():
        if not ligne["unit"].startswith("CP_MEUR:"):
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, libelle = _code_libelle(ligne["geo"])
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

        if ligne["na_item"].startswith("P61:"):
            exports[(code, annee)] = valeur
        elif ligne["na_item"].startswith("P71:"):
            imports_[(code, annee)] = valeur
        elif ligne["na_item"].startswith("B1GQ:"):
            pib[(code, annee)] = valeur

    resultat: list[dict] = []
    cles = set(exports) & set(imports_) & set(pib)
    for code, annee in cles:
        valeur = arrondi(100.0 * (exports[(code, annee)] - imports_[(code, annee)]) / pib[(code, annee)], 2)
        resultat.append({"maille": "pays", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur})
        if code == "FR":
            resultat.append(
                {"maille": "france", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur}
            )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
