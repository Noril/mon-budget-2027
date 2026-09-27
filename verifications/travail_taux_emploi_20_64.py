"""Recalcul indépendant de travail.taux_emploi_20_64.

Eurostat lfsi_emp_a, indic_em = EMP_LFS, sex = T, age = Y20-64, unit = PC_POP. Valeur =
OBS_VALUE telle quelle ; observations vides exclues. Code pays = partie de geo avant « : ».
Maille france = ligne geo FR recopiée avec le code FR.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-lfsi-emp-a.parquet"


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
        if not ligne["indic_em"].startswith("EMP_LFS:"):
            continue
        if ligne["sex"] != "T:Total":
            continue
        if not ligne["age"].startswith("Y20-64:"):
            continue
        if not ligne["unit"].startswith("PC_POP:"):
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
