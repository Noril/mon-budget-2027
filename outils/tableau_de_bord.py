"""Tableau de bord global : une ligne par indicateur calculé, regroupées par domaine.

    uv run python -m outils.tableau_de_bord      # écrit build/tableau-de-bord.md et data/tableau_de_bord.json

Pour chaque indicateur : dernière valeur France, évolution sur cinq périodes, valeur UE27 et rang de la France
parmi les 27 (quand la maille pays existe), écart entre départements (quand la maille département existe).
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from pipelines.commun import INDICATEURS_CALCULES, RACINE, charger_catalogue, definitions_indicateurs, ecrire_json

UE27 = "AT BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK".split()
SORTIE = RACINE / "build" / "tableau-de-bord.md"


def _valeur(table: Path, maille: str, code: str, periode: str) -> float | None:
    ligne = duckdb.execute(
        f"SELECT valeur FROM read_parquet('{table}') WHERE maille = ? AND code = ? AND periode = ?",
        [maille, code, periode],
    ).fetchone()
    return ligne[0] if ligne else None


def resumer(definition: dict, table: Path) -> dict:
    t = f"read_parquet('{table}')"
    periodes_fr = [p for (p,) in duckdb.sql(
        f"SELECT DISTINCT periode FROM {t} WHERE maille = 'france' AND valeur IS NOT NULL ORDER BY periode"
    ).fetchall()]
    r = {"id": definition["id"], "libelle": definition["libelle"], "unite": definition["unite"], "sens": definition["sens"]}
    if periodes_fr:
        derniere = periodes_fr[-1]
        avant = periodes_fr[-6] if len(periodes_fr) >= 6 else periodes_fr[0]
        r |= {"periode": derniere, "france": _valeur(table, "france", "FR", derniere)}
        if avant != derniere:
            r |= {"periode_avant": avant, "france_avant": _valeur(table, "france", "FR", avant)}

    if "pays" in definition["maille"]:
        # Dernière période où la France et la moyenne UE sont toutes deux publiées, sinon la dernière de la France
        (p_ue,) = duckdb.sql(
            f"""SELECT coalesce(
                    (SELECT max(periode) FROM {t} WHERE maille = 'pays' AND code = 'FR' AND valeur IS NOT NULL
                       AND periode IN (SELECT periode FROM {t} WHERE maille = 'pays' AND code = 'EU27_2020'
                                       AND valeur IS NOT NULL)),
                    (SELECT max(periode) FROM {t} WHERE maille = 'pays' AND code = 'FR' AND valeur IS NOT NULL))"""
        ).fetchone()
        if p_ue:
            pays = dict(duckdb.execute(
                f"SELECT code, valeur FROM {t} WHERE maille = 'pays' AND periode = ? AND valeur IS NOT NULL", [p_ue]
            ).fetchall())
            membres = {c: v for c, v in pays.items() if c in UE27}
            r |= {"periode_ue": p_ue, "fr_ue": pays.get("FR"), "ue27": pays.get("EU27_2020"), "nb_pays": len(membres)}
            if definition["sens"] != "neutre" and "FR" in membres:
                ordre = sorted(membres, key=membres.get, reverse=definition["sens"] == "plus_haut_mieux")
                r["rang_fr"] = ordre.index("FR") + 1

    if "departement" in definition["maille"] and periodes_fr:
        extremes = duckdb.execute(
            f"""SELECT arg_min(libelle, valeur), min(valeur), arg_max(libelle, valeur), max(valeur), count(*)
                FROM {t} WHERE maille = 'departement' AND periode = ? AND valeur IS NOT NULL""",
            [r["periode"]],
        ).fetchone()
        if extremes and extremes[4]:
            r |= {"dep_min": extremes[0], "val_min": extremes[1], "dep_max": extremes[2], "val_max": extremes[3],
                  "nb_dep": extremes[4]}
    return r


def _f(v: float | None) -> str:
    if v is None:
        return "—"
    chiffres = 0 if abs(v) >= 1000 else 1 if abs(v) >= 10 else 2
    return f"{v:,.{chiffres}f}".replace(",", " ").replace(".", ",")


def _ligne(r: dict) -> str:
    fr = f"{_f(r.get('france'))} ({r['periode']})" if "periode" in r else "—"
    evol = f"{_f(r['france_avant'])} en {r['periode_avant']}" if "france_avant" in r else "—"
    ue = f"UE {_f(r['ue27'])} ({r['periode_ue']})" if r.get("ue27") is not None else "—"
    rang = f"{r['rang_fr']}e / {r['nb_pays']}" if "rang_fr" in r else "—"
    dep = f"{r['dep_min']} {_f(r['val_min'])} → {r['dep_max']} {_f(r['val_max'])}" if "nb_dep" in r else "—"
    return f"| {r['libelle']} ({r['unite']}) | {fr} | {evol} | {ue} | {rang} | {dep} |"


def _sources(ids: set[str]) -> list[str]:
    """Mention de chaque source et de sa licence, exigée par les producteurs (OTAN, FMI, Parlement européen…)."""
    catalogue = charger_catalogue()
    lignes = ["", "## Sources et licences", "",
              "Valeurs calculées à partir des données des producteurs ci-dessous (données transformées : ratios, parts, "
              "agrégats) ; elles n'engagent pas ces producteurs. Conditions de réutilisation : `catalogue/`.", ""]
    for i in sorted(ids):
        if s := catalogue.get(i):
            lignes.append(f"- {s['producteur']}, {s['titre']} ({s['doc']}). Licence : {s['licence']}.")
    return lignes


def main() -> int:
    par_domaine: dict[str, list[dict]] = {}
    manquants = []
    sources_publiees: set[str] = set()
    for chemin, d in definitions_indicateurs():
        table = INDICATEURS_CALCULES / f"{d['id']}@{d['version']}.parquet"
        if not table.exists():
            manquants.append(d["id"])
            continue
        par_domaine.setdefault(chemin.parent.name, []).append(resumer(d, table))
        sources_publiees.update(d["sources"])

    lignes = [
        "# Tableau de bord global",
        "",
        "Généré par `outils.tableau_de_bord` à partir des indicateurs calculés. Rang : 1er = meilleure situation "
        "dans l'UE à 27, selon le sens de l'indicateur. Départements : le plus bas → le plus haut.",
    ]
    for domaine, resumes in sorted(par_domaine.items()):
        lignes += ["", f"## {domaine}", "", "| Indicateur | France | Il y a cinq périodes | UE27 | Rang de la France | Départements |",
                   "| --- | --- | --- | --- | --- | --- |"]
        lignes += [_ligne(r) for r in resumes]
    if manquants:
        lignes += ["", f"Indicateurs non calculés : {', '.join(manquants)}."]
    lignes += _sources(sources_publiees)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    ecrire_json(RACINE / "data" / "tableau_de_bord.json", {"domaines": par_domaine})
    print(f"  + {SORTIE.relative_to(RACINE)} ({sum(map(len, par_domaine.values()))} indicateurs, {len(par_domaine)} domaines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
