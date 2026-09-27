"""Fonctions communes aux vérifications immigration.*_ue (numérateur Eurostat / population Eurostat).

Ici, EU27_2020 est un code pays comme un autre (partie de geo avant « : ») : on utilise l'agrégat
publié par Eurostat directement (numérateur et population), sans le recalculer en sommant 27 pays.
C'est ce que demandent les YAML de ces indicateurs (« y compris les agrégats publiés par Eurostat »),
à la différence de justice.occupation_prisons_ue / justice.taux_detention_ue qui recalculent l'agrégat.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_POPULATION = NORMALISE / "eurostat-population-1er-janvier.parquet"


def lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def population() -> dict[tuple[str, str], float]:
    resultat: dict[tuple[str, str], float] = {}
    for ligne in lignes(FICHIER_POPULATION):
        if not ligne["indic_de"].startswith("JAN"):
            continue
        code, _, _ = ligne["geo"].partition(":")
        resultat[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])
    return resultat


def calculer_taux_pour_population(numerateur: dict[tuple[str, str], float], libelles: dict[str, str], multiplicateur: float) -> list[dict]:
    """numerateur[(code, annee)] -> valeur brute (code peut être 'EU27_2020', traité comme un pays).
    Rapporte à la population Eurostat (même code/année) et recopie la ligne FR sous la maille 'france'."""
    pop = population()
    resultat: list[dict] = []

    cles = set(numerateur) & set(pop)
    for code, annee in cles:
        taux = arrondi(multiplicateur * numerateur[(code, annee)] / pop[(code, annee)], 1)
        resultat.append({"maille": "pays", "code": code, "libelle": libelles.get(code, code), "periode": annee, "valeur": taux})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": taux})

    return resultat
