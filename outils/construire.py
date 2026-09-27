"""Résout les appels {{ind:…}} des fiches et écrit des pages Markdown dont chaque chiffre renvoie à son lignage.

    uv run python -m outils.construire      # écrit build/site/
"""

from __future__ import annotations

import sys

import duckdb

from pipelines.commun import INDICATEURS_CALCULES, RACINE, definitions_indicateurs, lire_json

from .fiches import appels, lire_fiche, toutes_les_fiches

SITE = RACINE / "build" / "site"


def resoudre(appel, definitions: dict) -> tuple[str, str]:
    """Renvoie (valeur formatée, note de lignage)."""
    nom = f"{appel.indicateur}@{appel.version}"
    table = INDICATEURS_CALCULES / f"{nom}.parquet"
    if not table.exists():
        raise LookupError(f"{nom} non calculé (lancer pipelines.indicateurs)")
    ligne = duckdb.execute(
        f"SELECT valeur, libelle FROM read_parquet('{table}') WHERE maille = ? AND code = ? AND periode = ?",
        [appel.maille, appel.code, appel.periode],
    ).fetchone()
    if ligne is None or ligne[0] is None:
        raise LookupError(f"aucune valeur pour {appel.texte}")
    d = definitions[appel.indicateur]
    lignage = lire_json(INDICATEURS_CALCULES / f"{nom}.lignage.json")
    sources = "; ".join(
        f"{m['producteur'].get('titre') or s} ({m['urls'][0]}), récupéré le {m['recupere_le']}, sha256 {m['sha256'][:12]}"
        for s, m in lignage["sources"].items()
    )
    note = (
        f"{d['libelle']}, {ligne[1]}, {appel.periode}. Indicateur `{nom}`, "
        f"formule `{d['formule']}` (sha256 {lignage['formule_sha256'][:12]}), calculé le {lignage['calcule_le']}. "
        f"Source : {sources}."
    )
    return d["format"].format(ligne[0]).replace(".", ","), note


def construire() -> list[str]:
    definitions = {d["id"]: d for _, d in definitions_indicateurs()}
    erreurs = []
    for chemin in toutes_les_fiches():
        entete, corps = lire_fiche(chemin)
        notes = []
        for a in appels(corps):
            try:
                valeur, note = resoudre(a, definitions)
            except LookupError as e:
                erreurs.append(f"{chemin.relative_to(RACINE)} : {e}")
                continue
            notes.append(note)
            corps = corps.replace(a.texte, f"{valeur}[^{len(notes)}]", 1)
        pied = "\n".join(f"[^{i}]: {n}" for i, n in enumerate(notes, 1))
        sortie = SITE / chemin.relative_to(RACINE)
        sortie.parent.mkdir(parents=True, exist_ok=True)
        sortie.write_text(f"# {entete['titre']}\n\n{corps.strip()}\n\n{pied}\n", encoding="utf-8")
        print(f"  + {sortie.relative_to(RACINE)} ({len(notes)} chiffres résolus)")
    return erreurs


def main() -> int:
    erreurs = construire()
    for e in erreurs:
        print(f"ERREUR {e}", file=sys.stderr)
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
