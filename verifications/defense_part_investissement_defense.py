"""Part de la FBCF (P51G) dans les dépenses totales (TE) de la fonction défense (GF02), Eurostat gov_10a_exp,
unit = MIO_EUR. Ratio non arrondi (montants en millions d'euros courants)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-gov-10a-exp-defense.parquet"


def _valeurs(na_item: str) -> dict[tuple[str, str], tuple[str, float]]:
    con = duckdb.connect()
    lignes = con.execute(
        f"""
        select geo, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where starts_with(unit, 'MIO_EUR:')
          and starts_with(sector, 'S13:')
          and starts_with(cofog99, 'GF02:')
          and starts_with(na_item, '{na_item}:')
          and OBS_VALUE is not null and trim(OBS_VALUE) != ''
        """
    ).fetchall()
    resultat: dict[tuple[str, str], tuple[str, float]] = {}
    for geo, periode, obs_value in lignes:
        code, _, libelle = geo.partition(":")
        resultat[(code, periode)] = (libelle, float(obs_value))
    return resultat


def calculer() -> list[dict]:
    p51g = _valeurs("P51G")
    te = _valeurs("TE")

    resultat: list[dict] = []
    for cle, (libelle, valeur_p51g) in p51g.items():
        if cle not in te:
            continue
        _, valeur_te = te[cle]
        if valeur_te == 0:
            continue
        code, periode = cle
        resultat.append(
            {
                "maille": "pays",
                "code": code,
                "libelle": libelle,
                "periode": periode,
                "valeur": 100 * valeur_p51g / valeur_te,
            }
        )

    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france", "libelle": "France"})

    return resultat
