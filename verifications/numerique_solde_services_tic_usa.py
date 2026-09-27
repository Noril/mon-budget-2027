"""Recalcul indépendant de numerique.solde_services_tic_usa.

Eurostat bop_its6_det, currency = MIO_EUR, bop_item = SI, stk_flow = BAL, partner = US.
Valeur = OBS_VALUE / 1000 (milliards d'euros), sans arrondi.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-bop-its6-det.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select currency, bop_item, stk_flow, partner, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not ligne["currency"].startswith("MIO_EUR:"):
            continue
        if not ligne["bop_item"].startswith("SI:"):
            continue
        if not ligne["stk_flow"].startswith("BAL:"):
            continue
        if not ligne["partner"].startswith("US:"):
            continue
        if ligne["OBS_VALUE"] is None or ligne["OBS_VALUE"] == "":
            continue
        valeur = float(ligne["OBS_VALUE"]) / 1000
        periode = ligne["TIME_PERIOD"]
        code, libelle = _code_libelle(ligne["geo"])
        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
