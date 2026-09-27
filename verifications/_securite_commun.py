"""Fonctions communes aux vérifications indépendantes des indicateurs securite.*

Lecture ligne à ligne de ssmsi-delinquance-departementale (pas de GROUP BY SQL) :
on accumule les numérateurs/dénominateurs en Python, département par département,
puis on calcule le taux pour 1000. Volontairement écrit sans recopier le SQL du
pipeline (non consulté).
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER_SSMSI = NORMALISE / "ssmsi-delinquance-departementale.parquet"
FICHIER_COG = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def libelles_departements() -> dict[str, str]:
    return {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_COG)}


def calculer_taux(indicateurs_retenus: set[str], denominateur_colonne: str) -> list[dict]:
    """indicateurs_retenus : valeurs de la colonne `indicateur` à sommer.
    denominateur_colonne : 'insee_pop' ou 'insee_log'.
    """
    libelles = libelles_departements()

    # numerateur[(dept, annee)] = somme des 'nombre' ; denom[(dept, annee)] = insee_pop/log (constant par dept-annee)
    numerateur: dict[tuple[str, str], int] = {}
    denominateur: dict[tuple[str, str], int] = {}

    for ligne in _lignes(FICHIER_SSMSI):
        if ligne["indicateur"] not in indicateurs_retenus:
            continue
        cle = (ligne["Code_departement"], ligne["annee"])
        numerateur[cle] = numerateur.get(cle, 0) + int(ligne["nombre"])
        denom_val = int(ligne[denominateur_colonne])
        if cle in denominateur and denominateur[cle] != denom_val:
            raise ValueError(f"dénominateur incohérent pour {cle}")
        denominateur[cle] = denom_val

    resultat: list[dict] = []
    # -- maille département --
    for (dept, annee), num in numerateur.items():
        denom = denominateur[(dept, annee)]
        valeur = arrondi(1000 * num / denom, 2)
        resultat.append(
            {
                "maille": "departement",
                "code": dept,
                "libelle": libelles.get(dept, dept),
                "periode": annee,
                "valeur": valeur,
            }
        )

    # -- maille France : somme des numérateurs / somme des dénominateurs, même année --
    par_annee_num: dict[str, int] = {}
    par_annee_denom: dict[str, int] = {}
    for (dept, annee), num in numerateur.items():
        par_annee_num[annee] = par_annee_num.get(annee, 0) + num
        par_annee_denom[annee] = par_annee_denom.get(annee, 0) + denominateur[(dept, annee)]

    for annee, num in par_annee_num.items():
        denom = par_annee_denom[annee]
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": annee,
                "valeur": arrondi(1000 * num / denom, 2),
            }
        )

    return resultat
