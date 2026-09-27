"""Recalcul indépendant de numerique.ia_generative_particuliers.

Eurostat isoc_ai_iaiu : particuliers ayant utilisé l'IA générative (I_IUAI), ind_type = IND_TOTAL, unit = PC_IND.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-isoc-ai-iaiu.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select ind_type, indic_is, unit, geo, TIME_PERIOD, OBS_VALUE from read_parquet('{FICHIER.as_posix()}')"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes():
        if not ligne["ind_type"].startswith("IND_TOTAL:"):
            continue
        if not ligne["indic_is"].startswith("I_IUAI:"):
            continue
        if not ligne["unit"].startswith("PC_IND:"):
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
