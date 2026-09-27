"""Recalcul indépendant de transports.annulations_ter à partir de sncf-regularite-ter.

Même rattachement des noms de region que transports.regularite_ter.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE
from verifications._arrondi import arrondi

FICHIER = NORMALISE / "sncf-regularite-ter.parquet"
FICHIER_COG = NORMALISE / "insee-cog-regions.parquet"

RATTACHEMENT_EXPLICITE = {
    "Rhône Alpes": "84",
    "Auvergne": "84",
    "Bourgogne": "27",
    "Franche Comté": "27",
    "Centre": "24",
    "Alsace": "44",
    "Lorraine": "44",
    "Champagne Ardenne": "44",
    "Nord Pas de Calais": "32",
    "Picardie": "32",
    "Haute Normandie": "28",
    "Basse Normandie": "28",
    "Aquitaine": "75",
    "Limousin": "75",
    "Poitou Charentes": "75",
    "Midi Pyrénées": "76",
    "Languedoc Roussillon": "76",
    "Etoile Amiens": "32",
    "Loire Océan": "52",
    "Sud Azur": "93",
    "Nouvelle Aquitaine": "75",
    "Centre Val-de-Loire": "24",
    "Pays-de-la-Loire": "52",
    "Provence Alpes Côte d'Azur": "93",
}


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_region(nom: str, libelle_vers_code: dict[str, str]) -> str | None:
    if nom in RATTACHEMENT_EXPLICITE:
        return RATTACHEMENT_EXPLICITE[nom]
    return libelle_vers_code.get(nom)


def calculer() -> list[dict]:
    cog = _lignes(FICHIER_COG)
    libelle_vers_code = {l["LIBELLE"]: l["REG"] for l in cog}
    libelle_par_code = {l["REG"]: l["LIBELLE"] for l in cog}

    par_region: dict[tuple[str, int], dict[int, tuple[float, float]]] = {}
    par_france: dict[int, dict[int, tuple[float, float]]] = {}

    for ligne in _lignes(FICHIER):
        if ligne["nombre_de_trains_annules"] is None:
            continue
        programmes = float(ligne["nombre_de_trains_programmes"])
        annules = float(ligne["nombre_de_trains_annules"])
        date = ligne["date"]
        annee, mois = date.year, date.month

        cur = par_france.setdefault(annee, {}).get(mois, (0.0, 0.0))
        par_france[annee][mois] = (cur[0] + programmes, cur[1] + annules)

        code = _code_region(ligne["region"], libelle_vers_code)
        if code is None:
            continue
        cle = (code, annee)
        cur = par_region.setdefault(cle, {}).get(mois, (0.0, 0.0))
        par_region[cle][mois] = (cur[0] + programmes, cur[1] + annules)

    resultat: list[dict] = []

    for annee, mois_valeurs in par_france.items():
        if len(mois_valeurs) != 12:
            continue
        programmes = sum(v[0] for v in mois_valeurs.values())
        annules = sum(v[1] for v in mois_valeurs.values())
        valeur = arrondi(100 * annules / programmes, 2)
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": str(annee), "valeur": valeur})

    for (code, annee), mois_valeurs in par_region.items():
        if annee < 2018:
            continue
        if len(mois_valeurs) != 12:
            continue
        programmes = sum(v[0] for v in mois_valeurs.values())
        annules = sum(v[1] for v in mois_valeurs.values())
        valeur = arrondi(100 * annules / programmes, 2)
        resultat.append(
            {
                "maille": "region",
                "code": code,
                "libelle": libelle_par_code.get(code, code),
                "periode": str(annee),
                "valeur": valeur,
            }
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
