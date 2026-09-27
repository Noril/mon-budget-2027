"""Agents des trois versants de la fonction publique (hors militaires), effectifs (pas de ratio).

Source insee-effectifs-fonction-publique (SIASP/TCRED), INDICATEUR=EFFECTIFS_FP_HMILIT_TOTAL, VERSANTS_FP=TOT,
SEXE=0. OBS_VALUE en milliers -> x1000, arrondi à l'unité (convention du dépôt : demi loin de zéro).
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "insee-effectifs-fonction-publique.parquet"


def _libelles_departements() -> dict[str, str]:
    con = duckdb.connect()
    lignes = con.execute(
        f"select DEP, LIBELLE from read_parquet('{(NORMALISE / 'insee-cog-departements.parquet').as_posix()}')"
    ).fetchall()
    return dict(lignes)


def _libelles_regions() -> dict[str, str]:
    con = duckdb.connect()
    lignes = con.execute(
        f"select REG, LIBELLE from read_parquet('{(NORMALISE / 'insee-cog-regions.parquet').as_posix()}')"
    ).fetchall()
    return dict(lignes)


def calculer() -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select REF_AREA, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where INDICATEUR = 'EFFECTIFS_FP_HMILIT_TOTAL' and VERSANTS_FP = 'TOT' and SEXE = '0'
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    dep_libelles = _libelles_departements()
    reg_libelles = _libelles_regions()

    resultat: list[dict] = []
    for ref_area, periode, obs_value in lignes:
        effectif = arrondi(float(obs_value) * 1000, 0)
        if ref_area == "FE":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": effectif})
        elif ref_area.startswith("D") and ref_area[1:] in dep_libelles:
            code = ref_area[1:]
            resultat.append(
                {"maille": "departement", "code": code, "libelle": dep_libelles[code], "periode": periode, "valeur": effectif}
            )
        elif ref_area.startswith("R") and ref_area[1:] in reg_libelles:
            code = ref_area[1:]
            resultat.append(
                {"maille": "region", "code": code, "libelle": reg_libelles[code], "periode": periode, "valeur": effectif}
            )
    return resultat
