"""Recalcul indépendant de energie.part_nucleaire_electricite à partir d'Eurostat nrg_bal_peh.

Regroupement en Python par (geo, période) pour retrouver siec N900H (nucléaire) et TOTAL.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-nrg-bal-peh.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    groupes: dict[tuple[str, str], dict[str, float]] = {}
    libelles: dict[str, str] = {}

    for ligne in _lignes():
        if not (ligne["nrg_bal"].startswith("GEP") and ligne["unit"].startswith("GWH")):
            continue
        siec_code = ligne["siec"].partition(":")[0]
        if siec_code not in ("N900H", "TOTAL"):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, _, libelle = ligne["geo"].partition(":")
        cle = (code, ligne["TIME_PERIOD"])
        groupes.setdefault(cle, {})[siec_code] = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

    resultat: list[dict] = []
    for (code, periode), valeurs in groupes.items():
        if "N900H" not in valeurs or "TOTAL" not in valeurs:
            continue
        total = valeurs["TOTAL"]
        if total == 0:
            continue
        part = 100 * valeurs["N900H"] / total
        libelle = libelles[code]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": part})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": part})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
