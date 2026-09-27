"""Recalcul indépendant de justice.places_operationnelles (Tab6, capacite_operationnelle, France entière)."""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "justice-ecroues-mensuel.parquet"


def calculer() -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(
        f"""
        select date_fichier, valeur
        from read_parquet('{FICHIER.as_posix()}')
        where tableau = 'Tab6' and mesure = 'capacite_operationnelle' and niveau = 'Total France entière'
        """
    )
    cols = [d[0] for d in cur.description]
    lignes = [dict(zip(cols, r)) for r in cur.fetchall()]

    resultat = []
    for ligne in lignes:
        periode = str(ligne["date_fichier"])[:7]
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": periode,
                "valeur": ligne["valeur"],
            }
        )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda r: r["periode"]):
        print(r)
