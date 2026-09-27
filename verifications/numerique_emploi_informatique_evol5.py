"""Recalcul indépendant de numerique.emploi_informatique_evol5.

Mêmes lecture, filtre et rattachement que numerique.emploi_informatique. Pour chaque territoire et chaque
année N à partir de 2011 : valeur = 100 * (effectifs N / effectifs N-5 - 1), arrondie à 0,1 ; territoire-année
exclu si l'année N-5 est absente ou nulle.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

from verifications.numerique_emploi_informatique import calculer as _effectifs


def calculer() -> list[dict]:
    par_territoire: dict[tuple[str, str], dict[int, float]] = {}
    for ligne in _effectifs():
        cle = (ligne["maille"], ligne["code"])
        par_territoire.setdefault(cle, {})[int(ligne["periode"])] = ligne["valeur"]

    resultat: list[dict] = []
    for (maille, code), par_annee in par_territoire.items():
        for annee, effectif_n in par_annee.items():
            if annee < 2011:
                continue
            effectif_n5 = par_annee.get(annee - 5)
            if not effectif_n5:  # absent ou nul
                continue
            valeur = arrondi(100 * (effectif_n / effectif_n5 - 1), 1)
            resultat.append({"maille": maille, "code": code, "libelle": code, "periode": str(annee), "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
