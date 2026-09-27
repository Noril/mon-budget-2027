"""Recalcul indépendant de immigration.taux_protection_global.

Numérateur = refugie + protection_subsidiaire + cnda_refugie + cnda_protection_subsidiaire ;
dénominateur = refugie + protection_subsidiaire + rejet (clôtures exclues). Valeur = 100 * num / denom,
arrondie à 0,1. Lignes à dénominateur nul exclues.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ofpra-decisions-departement.parquet"
FICHIER_COG = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _libelles_departements() -> dict[str, str]:
    return {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG)}


def _taux(ligne: dict) -> float | None:
    protections_ofpra = int(ligne["refugie"]) + int(ligne["protection_subsidiaire"])
    denominateur = protections_ofpra + int(ligne["rejet"])
    if denominateur == 0:
        return None
    numerateur = protections_ofpra + int(ligne["cnda_refugie"]) + int(ligne["cnda_protection_subsidiaire"])
    return arrondi(100 * numerateur / denominateur, 1)


def calculer() -> list[dict]:
    libelles = _libelles_departements()
    resultat: list[dict] = []

    for ligne in _lignes(FICHIER):
        taux = _taux(ligne)
        if taux is None:
            continue
        annee = ligne["annee_fichier"]

        if ligne["niveau"] == "Total":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": taux})
        elif ligne["niveau"] == "Département":
            code = ligne["code_departement"]
            if code in libelles:
                resultat.append(
                    {"maille": "departement", "code": code, "libelle": libelles[code], "periode": annee, "valeur": taux}
                )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
