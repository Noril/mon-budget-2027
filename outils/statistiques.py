"""Statistiques privées des parties du jeu enregistrées de façon anonyme (base Postgres Neon, jamais publiée).

    # .env.local (ignoré par git) : DATABASE_URL="postgres://…", chaîne de connexion copiée depuis la console Neon
    # (Vercel → Storage → la base → Open in Neon → Connect). Vercel marque la variable comme sensible : `vercel env pull`
    # ne la renvoie pas.
    uv run python -m outils.statistiques                      # répartition des choix, décision par décision
    uv run python -m outils.statistiques --croiser retraites-age taxes-energie
    uv run python -m outils.statistiques --themes                 # thèmes joués et étoilés, longueur des parties
    uv run python -m outils.statistiques --version 2026-11-03-themes   # une version du jeu seulement

Les parties antérieures au choix des thèmes (version sans suffixe « -themes ») ont joué toutes les questions ; leurs
colonnes themes et decisions sont vides. Les répartitions par levier ne comptent que les parties qui ont vu
le levier : une question d'un thème non choisi n'est pas « non vue » mais hors partie.

Échantillon auto-sélectionné (les joueurs du site) : ce ne sont pas des sondages, à ne jamais présenter comme
l'opinion des Français (loi n° 77-808 du 19 juillet 1977 relative aux sondages).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from urllib.parse import urlparse

import httpx

from pipelines.commun import RACINE

from .simulateur import lire_leviers


def url_base() -> str:
    url = os.environ.get("DATABASE_URL")
    fichier = RACINE / ".env.local"
    if not url and fichier.exists():
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("DATABASE_URL="):
                url = ligne.split("=", 1)[1].strip().strip('"')
    if not url or not url.startswith("postgres"):
        sys.exit("DATABASE_URL absent ou masqué : copiez la chaîne de connexion depuis la console Neon dans .env.local "
                 '(DATABASE_URL="postgres://…"), voir l\'en-tête de outils/statistiques.py')
    return url


def sql(requete: str, params: list | None = None) -> list[dict]:
    url = url_base()
    r = httpx.post(f"https://{urlparse(url).hostname}/sql", headers={"Neon-Connection-String": url},
                   json={"query": requete, "params": params or []}, timeout=30)
    r.raise_for_status()
    return r.json().get("rows", [])


def parties(version: str | None = None) -> list[dict]:
    # la table est créée par la fonction du site à la première partie enregistrée ; on la crée ici si besoin
    sql("""CREATE TABLE IF NOT EXISTS parties (id BIGSERIAL PRIMARY KEY, jour DATE NOT NULL DEFAULT CURRENT_DATE,
        version TEXT NOT NULL, choix JSONB NOT NULL)""")
    sql("ALTER TABLE parties ADD COLUMN IF NOT EXISTS themes JSONB, ADD COLUMN IF NOT EXISTS decisions INTEGER")
    if version:
        return sql("SELECT version, choix, themes, decisions FROM parties WHERE version = $1", [version])
    return sql("SELECT version, choix, themes, decisions FROM parties")


def avec_themes(p: dict) -> bool:
    return p.get("themes") is not None


def libelles() -> dict[str, tuple[str, dict[str, str]]]:
    return {l["id"]: (l["question"], {o["id"]: o["libelle"] for o in l.get("options", [])}) for l in lire_leviers()["leviers"]}


def repartition(version: str | None = None) -> None:
    lignes = parties(version)
    n = len(lignes)
    print(f"{n} parties enregistrées (joueurs du site : échantillon non représentatif)")
    for v, k in sorted(Counter(p["version"] for p in lignes).items()):
        print(f"  version {v} : {k}")
    print()
    if not n:
        return
    for id_levier, (question, options) in libelles().items():
        vues = [p for p in lignes if id_levier in p["choix"]]
        if not vues:
            continue
        valeurs = Counter(str(p["choix"][id_levier]) for p in vues)
        print(f"{question}  ({len(vues)} parties)")
        for v, k in valeurs.most_common():
            print(f"  {100 * k / len(vues):5.1f} %  {options.get(v, v)}")
        print()


def themes_joues(version: str | None = None) -> None:
    from .jeu import lire_cartes

    lignes = [p for p in parties(version) if avec_themes(p)]
    n = len(lignes)
    print(f"{n} parties avec choix des thèmes\n")
    if not n:
        return
    for t in lire_cartes()["themes"]:
        joue = sum(t["id"] in p["themes"] for p in lignes)
        etoile = sum(p["themes"].get(t["id"]) == 2 for p in lignes)
        print(f"  {t['nom'][:36]:36}  joué {100 * joue / n:5.1f} %   étoilé {100 * etoile / n:5.1f} %")
    tous = sum(len(p["themes"]) == len(lire_cartes()["themes"]) for p in lignes)
    decisions = sorted(p["decisions"] for p in lignes if p.get("decisions"))
    print(f"\n  tous les thèmes : {100 * tous / n:.1f} %")
    if decisions:
        print(f"  décisions par partie : médiane {decisions[len(decisions) // 2]}, min {decisions[0]}, max {decisions[-1]}")


def croiser(a: str, b: str) -> None:
    lib = libelles()
    table = Counter((str(p["choix"][a]), str(p["choix"][b])) for p in parties() if a in p["choix"] and b in p["choix"])
    totaux = Counter(x for x, _ in table.elements())
    print(f"{lib[a][0]}  ×  {lib[b][0]}\n")
    for (x, y), k in sorted(table.items(), key=lambda e: (-totaux[e[0][0]], -e[1])):
        print(f"  {lib[a][1].get(x, x)[:40]:40}  →  {lib[b][1].get(y, y)[:40]:40}  {100 * k / totaux[x]:5.1f} %  ({k})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--croiser", nargs=2, metavar=("LEVIER_A", "LEVIER_B"))
    parser.add_argument("--themes", action="store_true", help="thèmes joués et étoilés, longueur des parties")
    parser.add_argument("--version", help="ne garder qu'une version du jeu")
    args = parser.parse_args(argv)
    if args.croiser:
        croiser(*args.croiser)
    elif args.themes:
        themes_joues(args.version)
    else:
        repartition(args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
