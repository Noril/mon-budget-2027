"""Recalcul indépendant de numerique.locaux_fibre.

Source arcep-thd-deploiements-communes, une ligne par commune et par trimestre. Lignes dont locaux ou ftth
est vide exclues. Rattachement au département/région par le COG 2026 (voir verifications._cog). Valeur =
100 * somme(ftth) / somme(locaux) sur les communes du territoire, arrondie à 0,1. Maille France : toutes les
lignes retenues (même sans rattachement, ex. 977/978).
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE
from verifications._cog import libelles_dep, libelles_reg, rattachement_communes

FICHIER = NORMALISE / "arcep-thd-deploiements-communes.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select trimestre, code_commune, locaux, ftth from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    rattache = rattachement_communes()
    libelles_d = libelles_dep()
    libelles_r = libelles_reg()

    somme_dep: dict[tuple[str, str], list[float]] = {}
    somme_reg: dict[tuple[str, str], list[float]] = {}
    somme_france: dict[str, list[float]] = {}

    for l in _lignes():
        if l["locaux"] is None or l["ftth"] is None:
            continue
        trimestre = l["trimestre"]
        somme_france.setdefault(trimestre, [0.0, 0.0])
        somme_france[trimestre][0] += l["locaux"]
        somme_france[trimestre][1] += l["ftth"]

        dep_reg = rattache.get(l["code_commune"])
        if dep_reg is not None:
            dep, reg = dep_reg
            cle_dep = (dep, trimestre)
            somme_dep.setdefault(cle_dep, [0.0, 0.0])
            somme_dep[cle_dep][0] += l["locaux"]
            somme_dep[cle_dep][1] += l["ftth"]
            cle_reg = (reg, trimestre)
            somme_reg.setdefault(cle_reg, [0.0, 0.0])
            somme_reg[cle_reg][0] += l["locaux"]
            somme_reg[cle_reg][1] += l["ftth"]

    resultat: list[dict] = []
    for (dep, trimestre), (locaux, ftth) in somme_dep.items():
        valeur = arrondi(100 * ftth / locaux, 1)
        resultat.append({"maille": "departement", "code": dep, "libelle": libelles_d.get(dep, dep), "periode": trimestre, "valeur": valeur})
    for (reg, trimestre), (locaux, ftth) in somme_reg.items():
        valeur = arrondi(100 * ftth / locaux, 1)
        resultat.append({"maille": "region", "code": reg, "libelle": libelles_r.get(reg, reg), "periode": trimestre, "valeur": valeur})
    for trimestre, (locaux, ftth) in somme_france.items():
        valeur = arrondi(100 * ftth / locaux, 1)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": trimestre, "valeur": valeur})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
