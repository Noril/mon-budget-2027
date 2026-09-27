"""Aide partagée : agents FP (un indicateur/versant donné) pour 1 000 habitants (population au 1er janvier N+1)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

EFFECTIFS = NORMALISE / "insee-effectifs-fonction-publique.parquet"
POPULATION = NORMALISE / "insee-estimations-population.parquet"
COG_DEP = NORMALISE / "insee-cog-departements.parquet"
COG_REG = NORMALISE / "insee-cog-regions.parquet"


def _libelles(fichier, code_col, lib_col="LIBELLE") -> dict[str, str]:
    con = duckdb.connect()
    lignes = con.execute(f"select {code_col}, {lib_col} from read_parquet('{fichier.as_posix()}')").fetchall()
    return dict(lignes)


def _population(geo_object: str) -> dict[tuple[str, str], float]:
    """(GEO, TIME_PERIOD) -> population, pour EP_MEASURE=POP_JAN_1ST, AGE=_T, SEX=_T, un GEO_OBJECT donné.

    GEO_OBJECT doit être précisé : les codes numériques de département et de région se recoupent
    (departement 01 = Ain, région 01 = Guadeloupe), sans quoi les deux se mélangent dans le dictionnaire.
    """
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select GEO, TIME_PERIOD, OBS_VALUE
        from read_parquet('{POPULATION.as_posix()}')
        where EP_MEASURE = 'POP_JAN_1ST' and AGE = '_T' and SEX = '_T' and GEO_OBJECT = '{geo_object}'
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()
    return {(geo, periode): float(obs_value) for geo, periode, obs_value in lignes}


def calculer(indicateur: str, versant_fp: str) -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select REF_AREA, TIME_PERIOD, OBS_VALUE
        from read_parquet('{EFFECTIFS.as_posix()}')
        where INDICATEUR = '{indicateur}' and VERSANTS_FP = '{versant_fp}' and SEXE = '0'
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    dep_libelles = _libelles(COG_DEP, "DEP")
    reg_libelles = _libelles(COG_REG, "REG")
    pop_france = _population("FRANCE")
    pop_dep = _population("DEP")
    pop_reg = _population("REG")

    resultat: list[dict] = []
    for ref_area, periode, obs_value in lignes:
        effectif = float(obs_value) * 1000
        periode_suivante = str(int(periode) + 1)

        if ref_area == "FE":
            cle_pop = ("F_X_D976", periode_suivante)
            maille, code, libelle, pop = "france", "FR", "France", pop_france
        elif ref_area.startswith("D") and ref_area[1:] in dep_libelles:
            code = ref_area[1:]
            cle_pop = (code, periode_suivante)
            maille, libelle, pop = "departement", dep_libelles[code], pop_dep
        elif ref_area.startswith("R") and ref_area[1:] in reg_libelles:
            code = ref_area[1:]
            cle_pop = (code, periode_suivante)
            maille, libelle, pop = "region", reg_libelles[code], pop_reg
        else:
            continue

        if cle_pop not in pop or pop[cle_pop] == 0:
            continue  # année sans population N+1 publiée

        valeur = arrondi(1000 * effectif / pop[cle_pop], 2)
        resultat.append({"maille": maille, "code": code, "libelle": libelle, "periode": periode, "valeur": valeur})

    return resultat
