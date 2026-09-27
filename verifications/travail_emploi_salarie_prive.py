"""Recalcul indépendant de travail.emploi_salarie_prive.

Jeu URSSAF nombre-detablissements-employeurs-et-effectifs-salaries-du-secteur-prive-par-dep
(format large, urssaf-effectifs-departements). Chaque colonne effectifs_salaries_AAAA donne
l'année AAAA. Somme, par code_departement et année, de toutes les lignes (tous grands secteurs,
toutes tranches d'effectif, y compris "inconnu" et "nca"), valeurs vides ignorées. Maille
departement = code_departement présent comme DEP dans le COG 2026, libellé du COG. Maille
region = somme des départements par REG du COG 2026. Maille france = somme de toutes les
lignes. Arrondi à l'unité après sommation.
"""

from __future__ import annotations

import re

import math

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "urssaf-effectifs-departements.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _arrondi(x: float) -> int:
    # Demis arrondis en s'éloignant de zéro, comme l'exige la définition
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
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

    resultat: list[dict] = []
    par_region: dict[tuple[str, int], float] = {}
    par_france: dict[int, float] = {}

    for (code_dep, annee), total in par_departement.items():
        if code_dep in dep_info:
            reg, libelle_dep = dep_info[code_dep]
            resultat.append(
                {
                    "maille": "departement",
                    "code": code_dep,
                    "libelle": libelle_dep,
                    "periode": str(annee),
                    "valeur": _arrondi(total),
                }
            )
            par_region[(reg, annee)] = par_region.get((reg, annee), 0.0) + total
        par_france[annee] = par_france.get(annee, 0.0) + total

    for (reg, annee), total in par_region.items():
        resultat.append(
            {
                "maille": "region",
                "code": reg,
                "libelle": reg_libelle.get(reg, reg),
                "periode": str(annee),
                "valeur": _arrondi(total),
            }
        )

    for annee, total in par_france.items():
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": _arrondi(total)})

    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
