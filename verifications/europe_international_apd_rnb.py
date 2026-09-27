"""APD en % du RNB, OCDE DSD_DAC1@DF_DAC1. Deux définitions selon l'année : équivalent-don depuis 2018
(MEASURE=11002, FLOW_TYPE=1160) et versements nets avant (MEASURE=2, FLOW_TYPE=1140)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ocde-cad-apd-rnb.parquet"

CODE_PAYS = {
    "FRA": "FR", "DEU": "DE", "GRC": "EL", "GBR": "UK",
    "AUS": "AU", "AUT": "AT", "AZE": "AZ", "BEL": "BE", "BGR": "BG", "CAN": "CA",
    "CHE": "CH", "CYP": "CY", "CZE": "CZ", "DNK": "DK", "ESP": "ES", "EST": "EE",
    "FIN": "FI", "HRV": "HR", "HUN": "HU", "IRL": "IE", "ISL": "IS", "ISR": "IL",
    "ITA": "IT", "JPN": "JP", "KAZ": "KZ", "KOR": "KR", "KWT": "KW", "LIE": "LI",
    "LTU": "LT", "LUX": "LU", "LVA": "LV", "MCO": "MC", "MLT": "MT", "NLD": "NL",
    "NOR": "NO", "NZL": "NZ", "POL": "PL", "PRT": "PT", "QAT": "QA", "ROU": "RO",
    "SAU": "SA", "SVK": "SK", "SVN": "SI", "SWE": "SE", "THA": "TH", "TUR": "TR",
    "TWN": "TW", "USA": "US", "ARE": "AE",
}
AGREGATS = {"DAC", "DACEU", "DAC_EC", "G7"}


def calculer() -> list[dict]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select DONOR, Donor_1, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where SECTOR = '_Z' and TYING_STATUS = '_Z' and UNIT_MEASURE = 'PT_B5G' and PRICE_BASE = 'V'
          and (
                (TIME_PERIOD::int >= 2018 and MEASURE = '11002' and FLOW_TYPE = '1160')
             or (TIME_PERIOD::int <  2018 and MEASURE = '2'     and FLOW_TYPE = '1140')
          )
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()

    resultat: list[dict] = []
    for donor, libelle, periode, obs_value in lignes:
        if donor in AGREGATS:
            code = donor
        elif donor in CODE_PAYS:
            code = CODE_PAYS[donor]
        else:
            raise ValueError(f"donor non couvert : {donor!r}")
        resultat.append(
            {"maille": "pays", "code": code, "libelle": libelle, "periode": periode, "valeur": float(obs_value)}
        )

    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
