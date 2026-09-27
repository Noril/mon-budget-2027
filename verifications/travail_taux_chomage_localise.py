"""Recalcul indépendant de travail.taux_chomage_localise.

Flux BDM TAUX-CHOMAGE (insee-chomage-localise), séries INDICATEUR=TAUX_CHOMAGE_LOCALISE,
FREQ=T, CORRECTION=CVS ; OBS_VALUE vide ou NaN exclu ; valeur telle quelle. Période =
TIME_PERIOD avec "-Q" remplacé par "-T". Maille france = REF_AREA FR-D976, code FR. Maille
region = REF_AREA "R"+REG du COG 2026, libellé du COG. Maille departement = REF_AREA "D"+DEP du
COG 2026, libellé du COG. REF_AREA FM non repris.
"""

from __future__ import annotations

import math

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "insee-chomage-localise.parquet"
FICHIER_REG = NORMALISE / "insee-cog-regions.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _valeur_valide(obs_value) -> float | None:
    if obs_value is None:
        return None
    valeur = float(obs_value)
    if math.isnan(valeur):
        return None
    return valeur


def calculer() -> list[dict]:
    libelles_reg = {ligne["REG"]: ligne["LIBELLE"] for ligne in _lignes_brutes(FICHIER_REG)}
    libelles_dep = {ligne["DEP"]: ligne["LIBELLE"] for ligne in _lignes_brutes(FICHIER_DEP)}

    resultat: list[dict] = []
    for ligne in _lignes_brutes(FICHIER):
        if ligne["INDICATEUR"] != "TAUX_CHOMAGE_LOCALISE":
            continue
        if ligne["FREQ"] != "T":
            continue
        if ligne["CORRECTION"] != "CVS":
            continue

        valeur = _valeur_valide(ligne["OBS_VALUE"])
        if valeur is None:
            continue

        periode = ligne["TIME_PERIOD"].replace("-Q", "-T")
        ref_area = ligne["REF_AREA"]

        if ref_area == "FR-D976":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
        elif ref_area == "FM":
            continue
        elif ref_area.startswith("R") and ref_area[1:] in libelles_reg:
            reg = ref_area[1:]
            resultat.append(
                {"maille": "region", "code": reg, "libelle": libelles_reg[reg], "periode": periode, "valeur": valeur}
            )
        elif ref_area.startswith("D") and ref_area[1:] in libelles_dep:
            dep = ref_area[1:]
            resultat.append(
                {"maille": "departement", "code": dep, "libelle": libelles_dep[dep], "periode": periode, "valeur": valeur}
            )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
