"""Recalcul indépendant de sante.densite_mg_liberaux, ligne à ligne en Python."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "ameli-demographie-ps.parquet"

PROFESSION = "Ensemble des médecins généralistes"
CLASSE_AGE = "tout_age"
SEXE = "tout sexe"

CODE_REGION_FRANCE = "99"
CODE_DEPARTEMENT_AGREGAT = "999"


def _lignes_brutes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"""select * from read_parquet('{FICHIER.as_posix()}')
            where profession_sante = ? and classe_age = ? and libelle_sexe = ?""",
        [PROFESSION, CLASSE_AGE, SEXE],
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _classer(ligne: dict) -> tuple[str, str, str] | None:
    region, departement = ligne["region"], ligne["departement"]
    if region == CODE_REGION_FRANCE:
        return "france", "FR", "France"
    if departement == CODE_DEPARTEMENT_AGREGAT:
        return "region", region, ligne["libelle_region"]
    return "departement", departement, ligne["libelle_departement"]


def calculer() -> list[dict]:
    resultat: list[dict] = []
    for ligne in _lignes_brutes():
        if ligne["densite"] is None:
            continue
        maille, code, libelle = _classer(ligne)
        resultat.append(
            {
                "maille": maille,
                "code": code,
                "libelle": libelle,
                "periode": str(ligne["annee"].year),
                "valeur": ligne["densite"],
            }
        )
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
