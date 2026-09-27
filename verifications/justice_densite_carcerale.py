"""Recalcul indépendant de justice.densite_carcerale (Tab6, detenus / capacite_operationnelle, France entière)."""

from __future__ import annotations

from verifications._arrondi import arrondi

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "justice-ecroues-mensuel.parquet"


def calculer() -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(
        f"""
        select date_fichier, mesure, valeur
        from read_parquet('{FICHIER.as_posix()}')
        where tableau = 'Tab6' and mesure in ('detenus', 'capacite_operationnelle') and niveau = 'Total France entière'
        """
    )
    cols = [d[0] for d in cur.description]
    lignes = [dict(zip(cols, r)) for r in cur.fetchall()]

    par_classeur: dict[str, dict[str, float]] = {}
    for ligne in lignes:
        classeur = str(ligne["date_fichier"])[:10]
        par_classeur.setdefault(classeur, {})[ligne["mesure"]] = ligne["valeur"]

    resultat = []
    for classeur, valeurs in par_classeur.items():
        if "detenus" not in valeurs or "capacite_operationnelle" not in valeurs:
            continue
        periode = classeur[:7]
        taux = arrondi(100 * valeurs["detenus"] / valeurs["capacite_operationnelle"], 1)
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": periode,
                "valeur": taux,
            }
        )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda r: r["periode"]):
        print(r)
