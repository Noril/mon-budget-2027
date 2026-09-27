"""Recalcul indépendant de economie.productivite_horaire.

Eurostat nama_10_lp_ulc, unit = CP_MPPS_EU27_2020, na_item = NLPR_HW (productivité nominale par
heure travaillée). Valeur = OBS_VALUE tel quel ; observations vides exclues ; l'unité
PC_EU27_2020_MPPS_CP n'est pas utilisée. Code pays = partie de geo avant « : ». Maille france =
ligne geo FR recopiée avec le code FR.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-nama-10-lp-ulc.parquet"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        if not ligne["unit"].startswith("CP_MPPS_EU27_2020:"):
            continue
        if not ligne["na_item"].startswith("NLPR_HW:"):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, libelle = _code_libelle(ligne["geo"])
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": annee, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": code, "libelle": libelle, "periode": annee, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
