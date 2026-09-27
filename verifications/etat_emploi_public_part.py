"""Emploi public dans l'emploi total, OCDE DF_GOV_EMPPS_REP_YU, MEASURE=EMPG, SECTOR=S13.
Maille pays : UNIT_MEASURE=PT_EMP, valeur telle que publiée. Agrégat UE_OCDE (25 membres hors CY/MT) :
part pondérée par l'emploi total = 100 * sum(PS) / sum(100*PS/PT_EMP), années où les 25 ont PT_EMP et PS."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "ocde-emploi-public.parquet"

CODE_PAYS = {
    "AUS": "AU", "AUT": "AT", "BEL": "BE", "BGR": "BG", "CAN": "CA", "CHE": "CH",
    "CHL": "CL", "CRI": "CR", "CZE": "CZ", "DEU": "DE", "DNK": "DK", "ESP": "ES",
    "EST": "EE", "FIN": "FI", "FRA": "FR", "GBR": "UK", "GRC": "EL", "HRV": "HR",
    "HUN": "HU", "IRL": "IE", "ISL": "IS", "ISR": "IL", "ITA": "IT", "JPN": "JP",
    "KOR": "KR", "LTU": "LT", "LUX": "LU", "LVA": "LV", "MEX": "MX", "NLD": "NL",
    "NOR": "NO", "OECD_REP": "OCDE", "POL": "PL", "PRT": "PT", "ROU": "RO",
    "SVK": "SK", "SVN": "SI", "SWE": "SE", "TUR": "TR", "USA": "US",
}

MEMBRES_UE_25 = {
    "AT", "BE", "BG", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
    "IE", "IT", "LT", "LU", "LV", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
}


def calculer() -> list[dict]:
    con = duckdb.connect()
    lignes_pt = con.execute(
        f"""
        select REF_AREA, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where MEASURE = 'EMPG' and SECTOR = 'S13' and UNIT_MEASURE = 'PT_EMP'
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()
    lignes_ps = con.execute(
        f"""
        select REF_AREA, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where MEASURE = 'EMPG' and SECTOR = 'S13' and UNIT_MEASURE = 'PS'
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    resultat: list[dict] = []
    for ref_area, periode, obs_value in lignes_pt:
        if ref_area not in CODE_PAYS:
            continue
        resultat.append(
            {"maille": "pays", "code": CODE_PAYS[ref_area], "libelle": ref_area, "periode": periode, "valeur": float(obs_value)}
        )

    pt_emp: dict[tuple[str, str], float] = {}
    for ref_area, periode, obs_value in lignes_pt:
        if ref_area in CODE_PAYS:
            pt_emp[(CODE_PAYS[ref_area], periode)] = float(obs_value)
    ps: dict[tuple[str, str], float] = {}
    for ref_area, periode, obs_value in lignes_ps:
        if ref_area in CODE_PAYS:
            ps[(CODE_PAYS[ref_area], periode)] = float(obs_value)

    periodes = {p for (_, p) in pt_emp} | {p for (_, p) in ps}
    for periode in periodes:
        if not all((code, periode) in pt_emp and (code, periode) in ps for code in MEMBRES_UE_25):
            continue
        somme_ps = sum(ps[(code, periode)] for code in MEMBRES_UE_25)
        somme_emp_total = sum(100 * ps[(code, periode)] / pt_emp[(code, periode)] for code in MEMBRES_UE_25)
        resultat.append(
            {
                "maille": "pays",
                "code": "UE_OCDE",
                "libelle": "UE (25 membres)",
                "periode": periode,
                "valeur": arrondi(100 * somme_ps / somme_emp_total, 2),
            }
        )

    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
