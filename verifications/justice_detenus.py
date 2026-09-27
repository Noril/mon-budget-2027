"""Recalcul indépendant de justice.detenus (Tab2, mesure detenus, niveau France entière).

Un même mois (date) peut apparaître dans plusieurs classeurs (date_fichier) ; on
retient la valeur du classeur le plus récent, en Python, sans requête agrégée.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE

FICHIER = NORMALISE / "justice-ecroues-mensuel.parquet"


def _lignes() -> list[dict]:
    con = duckdb.connect()
    cur = con.execute(
        f"""
        select date_fichier, date, valeur
        from read_parquet('{FICHIER.as_posix()}')
        where tableau = 'Tab2' and mesure = 'detenus' and niveau = 'Total France entière'
        """
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def calculer() -> list[dict]:
    # pour chaque mois (date), on garde la ligne dont date_fichier est le plus récent
    retenu: dict[str, dict] = {}
    for ligne in _lignes():
        date = str(ligne["date"])[:10]
        date_fichier = str(ligne["date_fichier"])[:10]
        if date not in retenu or date_fichier > retenu[date]["date_fichier"]:
            retenu[date] = {"date_fichier": date_fichier, "valeur": ligne["valeur"]}

    resultat = []
    for date, info in retenu.items():
        periode = date[:7]  # AAAA-MM
        resultat.append(
            {
                "maille": "france",
                "code": "FR",
                "libelle": "France",
                "periode": periode,
                "valeur": info["valeur"],
            }
        )
    return resultat


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda r: r["periode"]):
        print(r)
