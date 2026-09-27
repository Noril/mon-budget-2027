from __future__ import annotations

from verifications._ce_budget_ue import contributions


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for (pays, annee), valeur in contributions().items():
        resultat.append({"maille": "pays", "code": pays, "libelle": pays, "periode": str(annee), "valeur": valeur})
    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france"})
    return resultat
