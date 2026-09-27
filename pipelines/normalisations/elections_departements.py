"""Résultats électoraux par département (ministère de l'Intérieur, data.gouv.fr) -> participation, format long.

Les fichiers changent d'un scrutin à l'autre : encodage (Latin-1 jusqu'en 2022, UTF-8 ensuite), guillemets,
libellés de colonnes (« Code du département » / « Code département »), codes des outre-mer (ZA… ou 971…),
zéro initial (« 1 » ou « 01 »). Seules les colonnes de participation sont gardées (inscrits, abstentions,
votants, blancs, nuls, exprimés) ; les voix par candidat, nuance ou liste sont écartées.

Scrutin, année et tour sont lus dans l'URL de la ressource (acces.urls, même ordre que les fichiers) :
dossier data.gouv.fr « election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour »…
Tour 1 par défaut (européennes : tour unique).

Codes départementaux normalisés sur le COG : 1 -> 01, ZA -> 971 (Guadeloupe), ZB -> 972, ZC -> 973,
ZD -> 974, ZM -> 976, ZS -> 975 (Saint-Pierre-et-Miquelon), ZW -> 986, ZP -> 987, ZN -> 988 ;
ZX (Saint-Martin et Saint-Barthélemy) et ZZ (Français établis hors de France) gardés tels quels.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import duckdb

OUTRE_MER = {"ZA": "971", "ZB": "972", "ZC": "973", "ZD": "974", "ZM": "976", "ZS": "975", "ZW": "986", "ZP": "987", "ZN": "988"}
COLONNES = {
    "code": ("Code du département", "Code département"),
    "libelle": ("Libellé du département", "Libellé département"),
    "inscrits": ("Inscrits",),
    "abstentions": ("Abstentions",),
    "votants": ("Votants",),
    "blancs": ("Blancs",),
    "nuls": ("Nuls",),
    "exprimes": ("Exprimés",),
}


def scrutin_annee_tour(url: str) -> tuple[str, int, int]:
    dossier = url.split("/resources/")[-1].split("/")[0] if "/resources/" in url else url
    scrutin = next((s for s in ("presidentielle", "legislatives", "europeennes") if s in dossier), None)
    annee = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", dossier)
    if scrutin is None or annee is None:
        raise ValueError(f"scrutin ou année illisible dans {url}")
    tour = 2 if re.search(r"(2nd|second|2e)-tour", dossier) else 1
    return scrutin, int(annee.group(1)), tour


def code_departement(brut: str) -> str:
    brut = brut.strip()
    if brut in OUTRE_MER:
        return OUTRE_MER[brut]
    return brut.zfill(2) if brut.isdigit() and len(brut) < 2 else brut


def lire(f: Path) -> list[list[str]]:
    octets = f.read_bytes()
    try:
        texte = octets.decode("utf-8-sig")
    except UnicodeDecodeError:
        texte = octets.decode("latin-1")
    return list(csv.reader(io.StringIO(texte), delimiter=";"))


def normaliser(source: dict, fichiers: list[Path], sortie: Path) -> None:
    urls = source["acces"]["urls"]
    if len(urls) != len(fichiers):
        raise ValueError(f"{source['id']} : {len(fichiers)} fichiers pour {len(urls)} URL")
    lignes = []
    for url, f in zip(urls, fichiers):
        scrutin, annee, tour = scrutin_annee_tour(url)
        entete, *corps = lire(f)
        entete = [c.strip() for c in entete]
        index = {}
        for cle, noms in COLONNES.items():
            trouve = [entete.index(n) for n in noms if n in entete]
            if not trouve:
                raise ValueError(f"{source['id']} : colonne {noms[0]!r} absente de {f.name}")
            index[cle] = trouve[0]
        for ligne in corps:
            if not ligne or not ligne[index["code"]].strip():
                continue
            v = {cle: ligne[i].strip() for cle, i in index.items()}
            lignes.append((
                scrutin, annee, tour, v["code"], code_departement(v["code"]), v["libelle"],
                *(int(v[c]) for c in ("inscrits", "abstentions", "votants", "blancs", "nuls", "exprimes")),
                f.name,
            ))
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (scrutin VARCHAR, annee INTEGER, tour INTEGER, code_brut VARCHAR, code_departement VARCHAR, "
        "libelle VARCHAR, inscrits BIGINT, abstentions BIGINT, votants BIGINT, blancs BIGINT, nuls BIGINT, "
        "exprimes BIGINT, fichier VARCHAR)"
    )
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", lignes)
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")
    con.close()
