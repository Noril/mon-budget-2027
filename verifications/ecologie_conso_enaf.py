"""Recalcul indépendant de ecologie.conso_enaf.

Source cerema-conso-enaf, une ligne par commune. Colonnes nafAAartBB avec BB = AA + 1 (naf11art12 ...
naf24art25), en m² : consommation affectée à l'année 20AA. Les colonnes pluriannuelles (naf11art21,
naf11art22, naf11art16, naf11art25, naf16art22, naf21art25) sont ignorées. Rattachement de idcom au
département par le COG 2026 (pas la colonne iddep de la source). Valeur = somme des m² / 10 000, arrondie à
0,1 ha. France (code FR) : toutes les communes, y compris celles non rattachées.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import re

import duckdb

from pipelines.commun import NORMALISE
from verifications._cog import libelles_dep, rattachement_communes

FICHIER = NORMALISE / "cerema-conso-enaf.parquet"
COLONNE_ANNUELLE = re.compile(r"^naf(\d\d)art(\d\d)$")


def _colonnes_annuelles(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    noms = [r[0] for r in con.execute(f"select column_name from (describe select * from read_parquet('{FICHIER.as_posix()}'))").fetchall()]
    colonnes = {}
    for nom in noms:
        m = COLONNE_ANNUELLE.match(nom)
        if m and int(m.group(2)) == int(m.group(1)) + 1:
            colonnes[nom] = 2000 + int(m.group(1))
    return colonnes


def calculer() -> list[dict]:
    con = duckdb.connect()
    colonnes = _colonnes_annuelles(con)
    rattache = rattachement_communes()
    libelles_d = libelles_dep()

    curseur = con.execute(f"select idcom, {', '.join(colonnes)} from read_parquet('{FICHIER.as_posix()}')")
    noms = [d[0] for d in curseur.description]
    lignes = [dict(zip(noms, ligne)) for ligne in curseur.fetchall()]

    somme_dep: dict[tuple[str, int], float] = {}
    somme_france: dict[int, float] = {}

    for l in lignes:
        dep_reg = rattache.get(l["idcom"])
        for colonne, annee in colonnes.items():
            brut = l[colonne]
            if brut is None or brut == "":
                continue
            m2 = float(brut)
            somme_france[annee] = somme_france.get(annee, 0.0) + m2
            if dep_reg is not None:
                dep, _ = dep_reg
                somme_dep[(dep, annee)] = somme_dep.get((dep, annee), 0.0) + m2

    resultat: list[dict] = []
    for (dep, annee), m2 in somme_dep.items():
        resultat.append({"maille": "departement", "code": dep, "libelle": libelles_d.get(dep, dep), "periode": str(annee), "valeur": arrondi(m2 / 10000, 1)})
    for annee, m2 in somme_france.items():
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": arrondi(m2 / 10000, 1)})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
