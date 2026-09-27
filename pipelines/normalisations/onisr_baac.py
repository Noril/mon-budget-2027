"""Fichiers annuels BAAC de l'ONISR : un fichier « caractéristiques » et un fichier « usagers » par année.

Sortie agrégée : annee, dep, tues, usagers — nombre d'usagers tués (grav = 2, décès dans les 30 jours)
et nombre total d'usagers impliqués, par année et département de l'accident. Le fichier des
caractéristiques porte le département (dep) ; celui des usagers la gravité (grav) ; la jointure se fait
sur l'identifiant d'accident (Num_Acc, nommé Accident_Id dans le fichier 2022). Le fichier 2019 écrit
les départements 01 à 09 sur un caractère : complétés à gauche par un zéro.
"""

from __future__ import annotations

import re
from pathlib import Path

import duckdb

ANNEE = re.compile(r"(20\d\d)\.csv$")


def _lire(chemin: Path) -> str:
    return f"read_csv('{chemin}', delim = ';', header = true, all_varchar = true, quote = '\"')"


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    par_annee: dict[str, dict[str, Path]] = {}
    for f in fichiers:
        if not (m := ANNEE.search(f.name)):
            raise ValueError(f"{source['id']} : année introuvable dans {f.name}")
        genre = "usagers" if f.name.startswith("usagers") else "caract"
        par_annee.setdefault(m.group(1), {})[genre] = f

    requetes = []
    for annee, f in sorted(par_annee.items()):
        if set(f) != {"caract", "usagers"}:
            raise ValueError(f"{source['id']} : fichiers incomplets pour {annee} ({sorted(f)})")
        colonnes = [c for (c,) in duckdb.sql(f"SELECT column_name FROM (DESCRIBE SELECT * FROM {_lire(f['caract'])})").fetchall()]
        ident = "Num_Acc" if "Num_Acc" in colonnes else "Accident_Id"
        requetes.append(
            f"""
            SELECT '{annee}' AS annee, CASE WHEN length(trim(c.dep)) = 1 THEN '0' || trim(c.dep) ELSE trim(c.dep) END AS dep,
                   count(*) FILTER (WHERE trim(u.grav) = '2') AS tues,
                   count(*) AS usagers
            FROM {_lire(f['usagers'])} AS u
            JOIN (SELECT {ident} AS Num_Acc, dep FROM {_lire(f['caract'])}) AS c USING (Num_Acc)
            GROUP BY ALL
            """
        )
    duckdb.sql(f"COPY ({' UNION ALL '.join(requetes)} ORDER BY annee, dep) TO '{sortie}' (FORMAT parquet)")
