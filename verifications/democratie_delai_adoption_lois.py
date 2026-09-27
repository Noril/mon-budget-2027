"""Recalcul indépendant de democratie.delai_adoption_lois à partir de an-dossiers-legislatifs.

Même champ que democratie.lois_promulguees, en écartant en plus les lignes dont date_promulgation
ne commence pas par l'année du code_loi. Par code_loi : promulgation = min(date_promulgation),
dépôt = min(date_premier_depot). Délai = promulgation - dépôt (jours). Valeur = médiane par année
(moyenne des deux valeurs centrales si nombre pair, comme DuckDB MEDIAN).
"""

from __future__ import annotations

import datetime as dt

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "an-dossiers-legislatifs.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _mediane(valeurs: list[float]) -> float:
    v = sorted(valeurs)
    n = len(v)
    milieu = n // 2
    if n % 2 == 1:
        return v[milieu]
    return (v[milieu - 1] + v[milieu]) / 2


def calculer() -> list[dict]:
    # code_loi -> liste des (date_promulgation, date_premier_depot) après filtres
    par_code: dict[str, list[tuple[str, str | None]]] = {}

    for ligne in _lignes():
        code_loi = ligne["code_loi"]
        if not code_loi:
            continue
        titre = ligne["titre_loi"] or ""
        if titre.strip().lower().startswith("autorisant"):
            continue
        date_promulgation = ligne["date_promulgation"]
        annee_code = code_loi[:4]
        if not date_promulgation or not date_promulgation.startswith(annee_code):
            continue
        par_code.setdefault(code_loi, []).append((date_promulgation, ligne["date_premier_depot"]))

    delais_par_annee: dict[str, list[float]] = {}
    for code_loi, lignes in par_code.items():
        promulgation = min(l[0] for l in lignes)
        depots = [l[1] for l in lignes if l[1]]
        if not depots:
            continue
        depot = min(depots)
        d_prom = dt.date.fromisoformat(promulgation)
        d_dep = dt.date.fromisoformat(depot)
        delai = (d_prom - d_dep).days
        annee = code_loi[:4]
        delais_par_annee.setdefault(annee, []).append(float(delai))

    annee_max = max(int(a) for a in delais_par_annee)
    resultat: list[dict] = []
    for annee, delais in delais_par_annee.items():
        if not (2018 <= int(annee) <= annee_max - 1):
            continue
        resultat.append(
            {"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": _mediane(delais)}
        )

    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: x["periode"]):
        print(r)
