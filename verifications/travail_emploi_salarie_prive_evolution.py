"""Recalcul indépendant de travail.emploi_salarie_prive_evolution.

Mêmes effectifs que travail.emploi_salarie_prive, avant arrondi : somme de toutes les lignes du
jeu URSSAF par code_departement et année, puis par REG du COG 2026 (region) et pour toutes les
lignes (france, code FR) ; departement = codes présents comme DEP dans le COG 2026. Valeur de
l'année N = 100 * (effectif N / effectif N-1 - 1), arrondie à 2 décimales ; pas de valeur si
l'effectif N-1 est nul ou absent. Première année calculée : 2007.
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import re

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "urssaf-effectifs-departements.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _effectifs_bruts() -> tuple[dict[tuple[str, int], float], dict[tuple[str, int], float], dict[int, float], dict, dict]:
    lignes = _lignes_brutes(FICHIER)
    dep_info = {ligne["DEP"]: (ligne["REG"], ligne["LIBELLE"]) for ligne in _lignes_brutes(FICHIER_DEP)}
    reg_libelle = {ligne["REG"]: ligne["LIBELLE"] for ligne in _lignes_brutes(NORMALISE / "insee-cog-regions.parquet")}

    colonnes_annees = sorted(
        int(m.group(1)) for c in lignes[0].keys() if (m := re.fullmatch(r"effectifs_salaries_(\d{4})", c))
    )

    par_departement: dict[tuple[str, int], float] = {}
    for ligne in lignes:
        code_dep = ligne["code_departement"]
        for annee in colonnes_annees:
            valeur = ligne.get(f"effectifs_salaries_{annee}")
            if valeur is None:
                continue
            cle = (code_dep, annee)
            par_departement[cle] = par_departement.get(cle, 0.0) + float(valeur)

    par_region: dict[tuple[str, int], float] = {}
    par_france: dict[int, float] = {}
    for (code_dep, annee), total in par_departement.items():
        if code_dep in dep_info:
            reg, _ = dep_info[code_dep]
            par_region[(reg, annee)] = par_region.get((reg, annee), 0.0) + total
        par_france[annee] = par_france.get(annee, 0.0) + total

    return par_departement, par_region, par_france, dep_info, reg_libelle


def calculer() -> list[dict]:
    par_departement, par_region, par_france, dep_info, reg_libelle = _effectifs_bruts()

    resultat: list[dict] = []

    for (code_dep, annee), effectif in par_departement.items():
        if code_dep not in dep_info:
            continue
        precedent = par_departement.get((code_dep, annee - 1))
        if precedent is None or precedent == 0:
            continue
        _, libelle = dep_info[code_dep]
        valeur = arrondi(100.0 * (effectif / precedent - 1.0), 2)
        resultat.append(
            {"maille": "departement", "code": code_dep, "libelle": libelle, "periode": str(annee), "valeur": valeur}
        )

    for (reg, annee), effectif in par_region.items():
        precedent = par_region.get((reg, annee - 1))
        if precedent is None or precedent == 0:
            continue
        valeur = arrondi(100.0 * (effectif / precedent - 1.0), 2)
        resultat.append(
            {"maille": "region", "code": reg, "libelle": reg_libelle.get(reg, reg), "periode": str(annee), "valeur": valeur}
        )

    for annee, effectif in par_france.items():
        precedent = par_france.get(annee - 1)
        if precedent is None or precedent == 0:
            continue
        valeur = arrondi(100.0 * (effectif / precedent - 1.0), 2)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": valeur})

    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
