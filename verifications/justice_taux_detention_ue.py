"""Recalcul indépendant de justice.taux_detention_ue (Eurostat crim_pris_cap / demo_gind JAN)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_PRISONS = NORMALISE / "eurostat-crim-pris-cap.parquet"
FICHIER_POPULATION = NORMALISE / "eurostat-population-1er-janvier.parquet"

EU27 = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
    "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK",
}


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def calculer() -> list[dict]:
    detenus: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}
    for ligne in _lignes(FICHIER_PRISONS):
        if not ligne["indic_cr"].startswith("PRIS_ACT_CAP"):
            continue
        if not ligne["unit"].startswith("NR"):
            continue
        code, _, libelle = ligne["geo"].partition(":")
        libelles[code] = libelle
        detenus[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    population: dict[tuple[str, str], float] = {}
    for ligne in _lignes(FICHIER_POPULATION):
        if not ligne["indic_de"].startswith("JAN"):
            continue
        code, _, _ = ligne["geo"].partition(":")
        population[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    resultat: list[dict] = []
    cles = set(detenus) & set(population)
    for code, annee in cles:
        taux = arrondi(100_000 * detenus[(code, annee)] / population[(code, annee)], 1)
        resultat.append(
            {"maille": "pays", "code": code, "libelle": libelles.get(code, code), "periode": annee, "valeur": taux}
        )
        if code == "FR":
            resultat.append(
                {"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": taux}
            )

    annees = {a for (_, a) in cles}
    for annee in annees:
        pays_ok = {p for p in EU27 if (p, annee) in detenus and (p, annee) in population}
        if pays_ok != EU27:
            continue
        somme_det = sum(detenus[(p, annee)] for p in EU27)
        somme_pop = sum(population[(p, annee)] for p in EU27)
        resultat.append(
            {
                "maille": "pays",
                "code": "EU27_2020",
                "libelle": "Union européenne - 27 pays (à partir de 2020)",
                "periode": annee,
                "valeur": arrondi(100_000 * somme_det / somme_pop, 1),
            }
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
