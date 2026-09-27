"""Recalcul indépendant de sante.ald_sans_mt à partir du Parquet normalisé.

Démarche volontairement différente d'une requête SQL agrégée : on lit les lignes
brutes une par une et on les classe en Python (règles explicites), sans GROUP BY.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ameli-ald-sans-mt.parquet"

CODE_REGION_FRANCE = "99"
CODE_DEPARTEMENT_AGREGAT = "999"
CODE_INCONNU = "inconnu"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _classer(ligne: dict) -> tuple[str, str, str] | None:
    """Renvoie (maille, code, libelle) pour une ligne exploitable, ou None si elle est à écarter."""
    region, departement = ligne["region"], ligne["departement"]

    if region == CODE_INCONNU or departement == CODE_INCONNU:
        return None  # territoire non identifié par le producteur

    if ligne["taux_patients_ald_sans_mt_integer"] is None:
        return None  # valeur masquée (« NC »)

    if region == CODE_REGION_FRANCE:
        return "france", "FR", "France"

    if departement == CODE_DEPARTEMENT_AGREGAT:
        return "region", region, ligne["libelle_region"]

    return "departement", departement, ligne["libelle_departement"]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        classement = _classer(ligne)
        if classement is None:
            continue
        maille, code, libelle = classement
        resultat.append(
            {
                "maille": maille,
                "code": code,
                "libelle": libelle,
                "periode": ligne["annee"],
                "valeur": ligne["taux_patients_ald_sans_mt_integer"],
            }
        )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
