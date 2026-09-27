"""Recalcul indépendant de economie.inflation_ipc.

Jeu Melodi DS_IPC_PRINC (insee-ipc). Lignes IDX_TYPE=CPI, IND_TYPE=Y_VAR (variation annuelle
moyenne, %), FREQ=A, COICOP_2018=00 (ensemble), TPH_CPI=_T (tous ménages), SEASONAL_ADJUST=N,
PRODUCT_GROUP=_Z ; OBS_VALUE vide exclu. Valeur = OBS_VALUE tel quel. Maille france = GEO=F, code
FR. Maille departement = GEO présent dans la colonne DEP du COG 2026, libellé du COG. GEO=FM non
repris.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER_IPC = NORMALISE / "insee-ipc.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    libelles_dep = {ligne["DEP"]: ligne["LIBELLE"] for ligne in _lignes_brutes(FICHIER_DEP)}

    resultat: list[dict] = []
    for ligne in _lignes_brutes(FICHIER_IPC):
        if ligne["IDX_TYPE"] != "CPI":
            continue
        if ligne["IND_TYPE"] != "Y_VAR":
            continue
        if ligne["FREQ"] != "A":
            continue
        if ligne["COICOP_2018"] != "00":
            continue
        if ligne["TPH_CPI"] != "_T":
            continue
        if ligne["SEASONAL_ADJUST"] != "N":
            continue
        if ligne["PRODUCT_GROUP"] != "_Z":
            continue
        if ligne["OBS_VALUE"] is None:
            continue

        geo = ligne["GEO"]
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])

        if geo == "F":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": valeur})
        elif geo == "FM":
            continue  # France métropolitaine non reprise
        elif geo in libelles_dep:
            resultat.append(
                {"maille": "departement", "code": geo, "libelle": libelles_dep[geo], "periode": annee, "valeur": valeur}
            )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
