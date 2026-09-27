from __future__ import annotations

from verifications._ce_budget_ue import contributions, depenses


def calculer() -> list[dict]:
    dep, contrib = depenses(), contributions()
    resultat: list[dict] = []
    for cle in dep.keys() & contrib.keys():
        pays, annee = cle
        resultat.append(
            {"maille": "pays", "code": pays, "libelle": pays, "periode": str(annee), "valeur": dep[cle] - contrib[cle]}
        )
    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france"})
    return resultat
