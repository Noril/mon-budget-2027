"""Statistiques privées des parties du jeu enregistrées avec consentement (base Postgres Neon, jamais publiée).

    # .env.local (ignoré par git) : DATABASE_URL="postgres://…", chaîne de connexion copiée depuis la console Neon
    # (Vercel → Storage → la base → Open in Neon → Connect). Vercel marque la variable comme sensible : `vercel env pull`
    # ne la renvoie pas.
    uv run python -m outils.statistiques                      # répartition des choix, décision par décision
    uv run python -m outils.statistiques --croiser retraites-age taxes-energie

Échantillon auto-sélectionné (les joueurs qui acceptent) : ce ne sont pas des sondages, à ne jamais présenter comme
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


def libelles() -> dict[str, tuple[str, dict[str, str]]]:
    return {l["id"]: (l["question"], {o["id"]: o["libelle"] for o in l.get("options", [])}) for l in lire_leviers()["leviers"]}


def repartition() -> None:
    parties = sql("SELECT choix FROM parties")
    n = len(parties)
    print(f"{n} parties enregistrées (échantillon de joueurs volontaires, non représentatif)\n")
    if not n:
        return
    for id_levier, (question, options) in libelles().items():
        valeurs = Counter(str(p["choix"].get(id_levier, "non vue")) for p in parties)
        print(question)
        for v, k in valeurs.most_common():
            print(f"  {100 * k / n:5.1f} %  {options.get(v, v)}")
        print()


def croiser(a: str, b: str) -> None:
    parties = sql("SELECT choix FROM parties")
    lib = libelles()
    table = Counter((str(p["choix"].get(a, "non vue")), str(p["choix"].get(b, "non vue"))) for p in parties)
    totaux = Counter(x for x, _ in table.elements())
    print(f"{lib[a][0]}  ×  {lib[b][0]}\n")
    for (x, y), k in sorted(table.items(), key=lambda e: (-totaux[e[0][0]], -e[1])):
        print(f"  {lib[a][1].get(x, x)[:40]:40}  →  {lib[b][1].get(y, y)[:40]:40}  {100 * k / totaux[x]:5.1f} %  ({k})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--croiser", nargs=2, metavar=("LEVIER_A", "LEVIER_B"))
    args = parser.parse_args(argv)
    croiser(*args.croiser) if args.croiser else repartition()
    return 0


if __name__ == "__main__":
    sys.exit(main())
