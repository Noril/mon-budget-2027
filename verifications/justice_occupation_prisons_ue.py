"""Recalcul indépendant de justice.occupation_prisons_ue (Eurostat crim_pris_cap)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "eurostat-crim-pris-cap.parquet"

EU27 = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
    "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
}


def _lignes() -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(
        f"""
        select indic_cr, unit, geo, TIME_PERIOD, OBS_VALUE
        from read_parquet('{FICHIER.as_posix()}')
        where unit like 'NR%'
        """
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def calculer() -> list[dict]:
    detenus: dict[tuple[str, str], float] = {}
    capacite: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}

    for ligne in _lignes():
        code, _, libelle = ligne["geo"].partition(":")
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])
        libelles[code] = libelle
        indic = ligne["indic_cr"]
        if indic.startswith("PRIS_ACT_CAP"):
            detenus[(code, annee)] = valeur
        elif indic.startswith("PRIS_OFF_CAP"):
            capacite[(code, annee)] = valeur

    resultat: list[dict] = []
    cles_pays = set(detenus) & set(capacite)
    for code, annee in cles_pays:
        taux = arrondi(100 * detenus[(code, annee)] / capacite[(code, annee)], 1)
        resultat.append(
            {"maille": "pays", "code": code, "libelle": libelles.get(code, code), "periode": annee, "valeur": taux}
        )
        if code == "FR":
            resultat.append(
                {"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": taux}
            )

    # agrégat EU27_2020 : uniquement les années où les 27 pays ont les deux valeurs
    annees = {a for (_, a) in cles_pays}
    for annee in annees:
        pays_ok = {p for p in EU27 if (p, annee) in detenus and (p, annee) in capacite}
        if pays_ok != EU27:
            continue
        somme_det = sum(detenus[(p, annee)] for p in EU27)
        somme_cap = sum(capacite[(p, annee)] for p in EU27)
        resultat.append(
            {
                "maille": "pays",
                "code": "EU27_2020",
                "libelle": "Union européenne - 27 pays (à partir de 2020)",
                "periode": annee,
                "valeur": arrondi(100 * somme_det / somme_cap, 1),
            }
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
