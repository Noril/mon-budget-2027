"""Recalcul indépendant de immigration.taux_execution_eloignements_ue.

Numérateur : migr_eirtn (retours). Dénominateur : migr_eiord (décisions), même code pays et même année.
EU27_2020 traité comme un pays (agrégat publié par Eurostat dans les deux sources, pas de somme recalculée).
Lignes à dénominateur nul exclues.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

from pipelines.commun import NORMALISE
from verifications._eurostat_ue_commun import lignes

FICHIER_EIRTN = NORMALISE / "eurostat-migr-eirtn.parquet"
FICHIER_EIORD = NORMALISE / "eurostat-migr-eiord.parquet"


def calculer() -> list[dict]:
    retours: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}
    for ligne in lignes(FICHIER_EIRTN):
        if not (ligne["citizen"].startswith("TOTAL") and ligne["c_dest"].startswith("TOTAL")
                and ligne["age"].startswith("TOTAL") and ligne["sex"].startswith("T") and ligne["unit"].startswith("PER")):
            continue
        code, _, libelle = ligne["geo"].partition(":")
        libelles[code] = libelle
        retours[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    decisions: dict[tuple[str, str], float] = {}
    for ligne in lignes(FICHIER_EIORD):
        if not (ligne["citizen"].startswith("TOTAL") and ligne["age"].startswith("TOTAL")
                and ligne["sex"].startswith("T") and ligne["unit"].startswith("PER")):
            continue
        code, _, libelle = ligne["geo"].partition(":")
        libelles.setdefault(code, libelle)
        decisions[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    resultat: list[dict] = []
    cles = set(retours) & set(decisions)
    for code, annee in cles:
        denom = decisions[(code, annee)]
        if denom == 0:
            continue
        taux = arrondi(100 * retours[(code, annee)] / denom, 1)
        resultat.append({"maille": "pays", "code": code, "libelle": libelles.get(code, code), "periode": annee, "valeur": taux})
        if code == "FR":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": taux})

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
