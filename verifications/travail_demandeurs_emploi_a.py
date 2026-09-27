"""Recalcul indépendant de travail.demandeurs_emploi_a.

Jeu DARES dares_defm_stock_region_cvs_trim (dares-defm-stock-trim) : type_de_donnees=cvs-cjo,
categorie=A, sexe=Total, tranche_d_age=Total, anciennete=Total ; valeur = nombre tel quel.
Période = date (AAAA-Tn). Maille france = code_region "Total France" et code_departement
"Total", code FR. Maille region = code_departement "Total" et code_region égal à un REG du COG
2026, libellé du COG. Maille departement = code_departement égal à un DEP du COG 2026, libellé
du COG. Ligne "Total France métropolitaine" non reprise.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "dares-defm-stock-trim.parquet"
FICHIER_REG = NORMALISE / "insee-cog-regions.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def calculer() -> list[dict]:
    libelles_reg = {ligne["REG"]: ligne["LIBELLE"] for ligne in _lignes_brutes(FICHIER_REG)}
    libelles_dep = {ligne["DEP"]: ligne["LIBELLE"] for ligne in _lignes_brutes(FICHIER_DEP)}

    resultat: list[dict] = []
    for ligne in _lignes_brutes(FICHIER):
        if ligne["type_de_donnees"] != "cvs-cjo":
            continue
        if ligne["categorie"] != "A":
            continue
        if ligne["sexe"] != "Total":
            continue
        if ligne["tranche_d_age"] != "Total":
            continue
        if ligne["anciennete"] != "Total":
            continue

        periode = ligne["date"]
        valeur = ligne["nombre_de_demandeurs_d_emploi"]
        code_region = ligne["code_region"]
        code_departement = ligne["code_departement"]

        if code_region == "Total France" and code_departement == "Total":
            resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": periode, "valeur": valeur})
        elif code_region == "Total France métropolitaine":
            continue
        elif code_departement == "Total" and code_region in libelles_reg:
            resultat.append(
                {
                    "maille": "region",
                    "code": code_region,
                    "libelle": libelles_reg[code_region],
                    "periode": periode,
                    "valeur": valeur,
                }
            )
        elif code_departement in libelles_dep:
            resultat.append(
                {
                    "maille": "departement",
                    "code": code_departement,
                    "libelle": libelles_dep[code_departement],
                    "periode": periode,
                    "valeur": valeur,
                }
            )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
