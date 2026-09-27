"""Recalcul indépendant de numerique.top500_puissance.

Source top500-listes : une ligne par supercalculateur et par liste (déjà les 500 machines de chaque liste).
Pour chaque liste : total = somme des Rmax des 500 machines ; part d'un pays = 100 * somme des Rmax des
machines de ce pays / total, arrondie à 0,01. Pays retenus : les 27 États membres de l'UE (Eurostat, Grèce =
EL), les États-Unis, la Chine, le Japon, le Royaume-Uni, la Corée du Sud, la Suisse, la Norvège.
EU27_2020 = somme des Rmax des 27 États membres / total (calculée avant arrondi, comme les parts nationales).
"""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "top500-listes.parquet"

# Les 27 Etats membres de l'UE (nom du pays dans TOP500 -> code Eurostat, Grece = EL)
PAYS_UE27 = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY",
    "Czechia": "CZ", "Denmark": "DK", "Estonia": "EE", "Finland": "FI", "France": "FR",
    "Germany": "DE", "Greece": "EL", "Hungary": "HU", "Ireland": "IE", "Italy": "IT",
    "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT", "Netherlands": "NL",
    "Poland": "PL", "Portugal": "PT", "Romania": "RO", "Slovakia": "SK", "Slovenia": "SI",
    "Spain": "ES", "Sweden": "SE",
}

AUTRES_PAYS = {
    "United States": "US", "China": "CN", "Japan": "JP", "United Kingdom": "UK",
    "South Korea": "KR", "Switzerland": "CH", "Norway": "NO",
}

TOUS_PAYS = {**PAYS_UE27, **AUTRES_PAYS}


def _lignes() -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select liste, pays, rmax_tflops from read_parquet('{FICHIER.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    par_liste: dict[str, dict[str, float]] = {}
    totaux: dict[str, float] = {}
    for ligne in _lignes():
        liste = ligne["liste"]
        rmax = ligne["rmax_tflops"] or 0.0
        totaux[liste] = totaux.get(liste, 0.0) + rmax
        par_liste.setdefault(liste, {})
        par_liste[liste][ligne["pays"]] = par_liste[liste].get(ligne["pays"], 0.0) + rmax

    resultat: list[dict] = []
    for liste, par_pays in par_liste.items():
        total = totaux[liste]
        somme_ue27 = 0.0
        for pays_nom, code in TOUS_PAYS.items():
            rmax_pays = par_pays.get(pays_nom)
            if rmax_pays is None:
                continue  # pays absent de cette liste : pas de ligne
            if code in PAYS_UE27.values():
                somme_ue27 += rmax_pays
            valeur = arrondi(100 * rmax_pays / total, 2)
            resultat.append({"maille": "pays", "code": code, "libelle": pays_nom, "periode": liste, "valeur": valeur})
            if code == "FR":
                resultat.append({"maille": "france", "code": "FR", "libelle": pays_nom, "periode": liste, "valeur": valeur})
        valeur_ue = arrondi(100 * somme_ue27 / total, 2)
        resultat.append({"maille": "pays", "code": "EU27_2020", "libelle": "Union européenne", "periode": liste, "valeur": valeur_ue})
    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
