"""Recalcul indépendant de agriculture.chefs_55_ans_et_plus.

Démarche : on regroupe en Python les lignes par (geo, période) pour retrouver les trois
tranches d'âge nécessaires (Y55-64, Y_GE65, TOTAL), sans GROUP BY SQL, puis on calcule
100 * (Y55-64 + Y_GE65) / TOTAL, sans arrondi.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-ef-m-farmang.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def _garde_geo(code: str) -> bool:
    return len(code) == 2 or code.startswith("EU")


def calculer() -> list[dict]:
    # (geo, periode) -> {age_code: valeur}
    groupes: dict[tuple[str, str], dict[str, float]] = {}
    libelles: dict[str, str] = {}

    for ligne in _lignes():
        if not (
            ligne["statinfo"].startswith("TOTAL")
            and ligne["sex"].startswith("T:")
            and ligne["so_eur"].startswith("TOTAL")
            and ligne["uaarea"].startswith("TOTAL")
            and ligne["unit"].startswith("HLD")
        ):
            continue
        age_code = ligne["age"].partition(":")[0]
        if age_code not in ("Y55-64", "Y_GE65", "TOTAL"):
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        code, libelle = _code_libelle(ligne["geo"])
        if not _garde_geo(code):
            continue

        cle = (code, ligne["TIME_PERIOD"])
        groupes.setdefault(cle, {})[age_code] = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

    resultat: list[dict] = []
    for (code, periode), valeurs in groupes.items():
        if not all(k in valeurs for k in ("Y55-64", "Y_GE65", "TOTAL")):
            continue
        total = valeurs["TOTAL"]
        part = 100 * (valeurs["Y55-64"] + valeurs["Y_GE65"]) / total
        libelle = libelles[code]

        resultat.append({"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": part})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": libelle, "periode": periode, "valeur": part})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
