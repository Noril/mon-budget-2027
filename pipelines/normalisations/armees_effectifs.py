"""Ministère des Armées : « Évolution de la répartition des militaires de carrière et sous contrat » (XLS).

Un onglet « Ensemble ». Deux lignes d'en-tête : armée (Terre, Marine, Air et Espace, Total 3 armées, Autres*,
Total (hors gendarmerie)), fusionnée sur deux colonnes, puis statut (Carrière, contrat). Pour chaque année, un
bloc de lignes : l'année (ou la catégorie : officiers, sous-officiers, militaires du rang, volontaires) en
première colonne, « effectif » ou « ratio carrière / contrat » en deuxième.

Sortie longue, lignes « effectif » seulement : annee, categorie (ensemble, officiers…), armee, statut, etpt.
Les cases vides (colonnes « Autres » et « Total » absentes en 2001) ne donnent pas de ligne.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import xlrd


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    classeurs = [f for f in fichiers if f.suffix == ".xls"]
    if len(classeurs) != 1:
        raise ValueError(f"{source['id']} : un classeur XLS attendu, {len(classeurs)} trouvés")
    feuille = xlrd.open_workbook(classeurs[0]).sheet_by_index(0)
    lignes = [feuille.row_values(i) for i in range(feuille.nrows)]
    i_statut = next(i for i, r in enumerate(lignes) if "Carrière" in r)
    armees, courante = {}, None
    for j, c in enumerate(lignes[i_statut - 1]):
        courante = str(c).replace("*", "").strip() or courante
        if j >= 2:
            armees[j] = courante
    statuts = {j: str(c).strip().lower() for j, c in enumerate(lignes[i_statut]) if j >= 2 and c}

    sortie_lignes, annee = [], None
    for r in lignes[i_statut + 1:]:
        if str(r[1]).strip() != "effectif":
            continue
        if isinstance(r[0], float):
            annee, categorie = int(r[0]), "ensemble"
        else:
            categorie = str(r[0]).strip()
        if annee is None:
            raise ValueError(f"{source['id']} : catégorie « {categorie} » avant toute année")
        for j, statut in statuts.items():
            if isinstance(r[j], float):
                sortie_lignes.append((annee, categorie, armees[j], statut, r[j]))
    con = duckdb.connect()
    con.execute("CREATE TABLE t (annee INTEGER, categorie VARCHAR, armee VARCHAR, statut VARCHAR, etpt DOUBLE)")
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?)", sortie_lignes)
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")
