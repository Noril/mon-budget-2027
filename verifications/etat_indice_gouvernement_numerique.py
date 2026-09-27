"""Indice DGI, OCDE DF_GOV_DGOGD_2025, MEASURE=DG, UNIT_MEASURE=IX. Valeur telle que publiée (3 décimales).
Maille pays : code ISO alpha-2 (convention Eurostat), OECD_REP -> OCDE. Agrégat UE_OCDE : moyenne simple des
membres de l'UE présents chaque année."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "ocde-gouvernement-numerique.parquet"

CODE_PAYS = {
    "ARG": "AR", "AUS": "AU", "AUT": "AT", "BEL": "BE", "BGR": "BG", "BRA": "BR",
    "CAN": "CA", "CHE": "CH", "CHL": "CL", "COL": "CO", "CRI": "CR", "CZE": "CZ",
    "DNK": "DK", "ESP": "ES", "EST": "EE", "FIN": "FI", "FRA": "FR", "GBR": "UK",
    "GRC": "EL", "HRV": "HR", "HUN": "HU", "IDN": "ID", "IRL": "IE", "ISL": "IS",
    "ISR": "IL", "ITA": "IT", "JPN": "JP", "KOR": "KR", "LTU": "LT", "LUX": "LU",
    "LVA": "LV", "MEX": "MX", "NLD": "NL", "NOR": "NO", "NZL": "NZ", "OECD_REP": "OCDE",
    "PER": "PE", "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "SWE": "SE", "THA": "TH", "TUR": "TR",
}

MEMBRES_UE = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR",
    "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
}


def calculer() -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select REF_AREA, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where MEASURE = 'DG' and UNIT_MEASURE = 'IX' and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    resultat: list[dict] = []
    par_periode_ue: dict[str, list[float]] = {}
    for ref_area, periode, obs_value in lignes:
        if ref_area not in CODE_PAYS:
            continue  # pays absent de la table de correspondance
        code = CODE_PAYS[ref_area]
        valeur = float(obs_value)
        resultat.append({"maille": "pays", "code": code, "libelle": ref_area, "periode": periode, "valeur": valeur})
        if code in MEMBRES_UE:
            par_periode_ue.setdefault(periode, []).append(valeur)

    for periode, valeurs in par_periode_ue.items():
        resultat.append(
            {
                "maille": "pays",
                "code": "UE_OCDE",
                "libelle": f"UE ({len(valeurs)} membres)",
                "periode": periode,
                "valeur": arrondi(sum(valeurs) / len(valeurs), 3),
            }
        )

    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
