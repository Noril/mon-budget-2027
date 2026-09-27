"""Recalcul indépendant de logement.prix_m2_logements.

Source dgfip-dvf-statistiques (lignes echelle_geo = nation ou departement), colonnes nb_ventes_apt_maison et
moy_prix_m2_apt_maison. Année = 4 premiers caractères de annee_mois ; seules les années dont les 12 mois
figurent pour la ligne nation sont retenues. Valeur annuelle = somme(nb_ventes * prix moyen) / somme(nb_ventes)
sur les mois de l'année où nb_ventes > 0 et le prix est renseigné, arrondie à l'euro.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "dgfip-dvf-statistiques.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(
        f"select echelle_geo, code_geo, annee_mois, nb_ventes_apt_maison, moy_prix_m2_apt_maison from read_parquet('{FICHIER.as_posix()}')"
    )
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    lignes = _lignes()

    mois_nation: dict[str, set[str]] = {}
    for l in lignes:
        if l["echelle_geo"] != "nation":
            continue
        annee = l["annee_mois"][:4]
        mois_nation.setdefault(annee, set()).add(l["annee_mois"])
    annees_retenues = {annee for annee, mois in mois_nation.items() if len(mois) == 12}

    accum: dict[tuple[str, str, str], list[float]] = {}  # (maille, code, annee) -> [ventes*prix, ventes]
    for l in lignes:
        annee = l["annee_mois"][:4]
        if annee not in annees_retenues:
            continue
        if l["nb_ventes_apt_maison"] in (None, ""):
            continue
        nb_ventes = float(l["nb_ventes_apt_maison"])
        if nb_ventes <= 0:
            continue
        if l["moy_prix_m2_apt_maison"] in (None, ""):
            continue
        prix = float(l["moy_prix_m2_apt_maison"])

        if l["echelle_geo"] == "nation":
            cle = ("france", "FR", annee)
        elif l["echelle_geo"] == "departement":
            cle = ("departement", l["code_geo"], annee)
        else:
            continue
        accum.setdefault(cle, [0.0, 0.0])
        accum[cle][0] += nb_ventes * prix
        accum[cle][1] += nb_ventes

    resultat: list[dict] = []
    for (maille, code, annee), (num, den) in accum.items():
        if den == 0:
            continue
        resultat.append({"maille": maille, "code": code, "libelle": code, "periode": annee, "valeur": arrondi(num / den)})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
