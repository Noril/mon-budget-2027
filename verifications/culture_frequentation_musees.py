"""Recalcul indépendant de culture.frequentation_musees."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "culture-frequentation-musees.parquet"
FICHIER_COMMUNES = NORMALISE / "insee-cog-communes.parquet"
FICHIER_DEP = NORMALISE / "insee-cog-departements.parquet"


def _lignes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _dep_par_commune() -> dict[str, str]:
    communes = _lignes(FICHIER_COMMUNES)
    dep_par_code: dict[str, str] = {}
    # COM et ARM : DEP direct, priorité en cas de doublon avec COMD/COMA.
    for l in communes:
        if l["TYPECOM"] in ("COM", "ARM") and l["DEP"] is not None:
            dep_par_code[l["COM"]] = l["DEP"]
    # COMD et COMA : héritent du DEP de leur COMPARENT.
    parent_par_code = {l["COM"]: l["COMPARENT"] for l in communes if l["TYPECOM"] in ("COMD", "COMA")}
    for code, parent in parent_par_code.items():
        if code in dep_par_code:
            continue  # déjà pourvu par une ligne COM/ARM
        if parent in dep_par_code:
            dep_par_code[code] = dep_par_code[parent]
    return dep_par_code


def _dep_repli(code: str) -> str:
    return code[:3] if code.startswith("97") else code[:2]


def calculer() -> list[dict]:
    dep_par_code = _dep_par_commune()
    dep_cog = {l["DEP"]: l["LIBELLE"] for l in _lignes(FICHIER_DEP)}

    par_annee_france: dict[str, int] = {}
    par_annee_dep: dict[tuple[str, str], int] = {}

    for ligne in _lignes(FICHIER):
        if ligne["total"] is None:
            continue
        total = int(ligne["total"])
        annee = ligne["annee"]

        par_annee_france[annee] = par_annee_france.get(annee, 0) + total

        code_commune = ligne["codeInseeCommune"]
        dep = dep_par_code.get(code_commune) or _dep_repli(code_commune)
        if dep in dep_cog:
            cle = (dep, annee)
            par_annee_dep[cle] = par_annee_dep.get(cle, 0) + total

    resultat: list[dict] = []
    for annee, total in par_annee_france.items():
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": float(total)})
    for (dep, annee), total in par_annee_dep.items():
        resultat.append(
            {"maille": "departement", "code": dep, "libelle": dep_cog[dep], "periode": annee, "valeur": float(total)}
        )

    return resultat


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
