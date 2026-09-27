from __future__ import annotations

from verifications._ce_budget_ue import contributions, depenses, rnb


def calculer() -> list[dict]:
    dep, contrib, revenu = depenses(), contributions(), rnb()
    resultat: list[dict] = []
    for cle in dep.keys() & contrib.keys() & revenu.keys():
        pays, annee = cle
        if revenu[cle] == 0:
            continue
        resultat.append(
            {
                "maille": "pays",
                "code": pays,
                "libelle": pays,
                "periode": str(annee),
                "valeur": 100 * (dep[cle] - contrib[cle]) / revenu[cle],
            }
        )
    for ligne in list(resultat):
        if ligne["code"] == "FR":
            resultat.append({**ligne, "maille": "france"})
    return resultat
