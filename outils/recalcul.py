"""Recalcul indépendant d'un indicateur et comparaison avec le Parquet calculé par le pipeline.

    uv run python -m outils.recalcul sante.ald_sans_mt
"""

from __future__ import annotations

import importlib
import importlib.util
import sys

import duckdb

from pipelines.commun import INDICATEURS_CALCULES, definitions_indicateurs, ecrire_json, maintenant

TOLERANCE = 1e-6


def _definition(id_indicateur: str) -> dict:
    for _, d in definitions_indicateurs():
        if d.get("id") == id_indicateur:
            return d
    raise SystemExit(f"indicateur inconnu au catalogue : {id_indicateur}")


def _table_calculee(id_indicateur: str, version: str) -> dict[tuple[str, str, str], float]:
    fichier = INDICATEURS_CALCULES / f"{id_indicateur}@{version}.parquet"
    if not fichier.exists():
        raise SystemExit(f"fichier introuvable : {fichier}")
    con = duckdb.connect()
    lignes = con.execute(f"select maille, code, periode, valeur from read_parquet('{fichier.as_posix()}')").fetchall()
    return {(m, c, p): v for m, c, p, v in lignes}


def _table_recalculee(module) -> dict[tuple[str, str, str], float]:
    lignes = module.calculer()
    return {(l["maille"], l["code"], l["periode"]): l["valeur"] for l in lignes}


def comparer(attendu: dict[tuple[str, str, str], float], recalcule: dict[tuple[str, str, str], float]) -> dict:
    cles_attendu, cles_recalcule = set(attendu), set(recalcule)

    seulement_attendu = sorted(cles_attendu - cles_recalcule)
    seulement_recalcule = sorted(cles_recalcule - cles_attendu)
    valeurs_differentes = []
    for cle in sorted(cles_attendu & cles_recalcule):
        v_attendu, v_recalcule = attendu[cle], recalcule[cle]
        if abs(v_attendu - v_recalcule) > TOLERANCE:
            valeurs_differentes.append(
                {"maille": cle[0], "code": cle[1], "periode": cle[2], "attendu": v_attendu, "recalcule": v_recalcule}
            )

    return {
        "lignes_comparees": len(cles_attendu | cles_recalcule),
        "seulement_dans_attendu": [{"maille": c[0], "code": c[1], "periode": c[2]} for c in seulement_attendu],
        "seulement_dans_recalcule": [{"maille": c[0], "code": c[1], "periode": c[2]} for c in seulement_recalcule],
        "valeurs_differentes": valeurs_differentes,
    }


def _rapport_texte(id_indicateur: str, version: str, ecarts: dict) -> str:
    lignes = [f"Recalcul de {id_indicateur}@{version} : {ecarts['lignes_comparees']} lignes comparées."]
    if ecarts["seulement_dans_attendu"]:
        lignes.append(f"- {len(ecarts['seulement_dans_attendu'])} ligne(s) présente(s) seulement dans le fichier calculé :")
        for c in ecarts["seulement_dans_attendu"]:
            lignes.append(f"    manque au recalcul : {c['maille']} {c['code']} {c['periode']}")
    if ecarts["seulement_dans_recalcule"]:
        lignes.append(f"- {len(ecarts['seulement_dans_recalcule'])} ligne(s) présente(s) seulement dans le recalcul :")
        for c in ecarts["seulement_dans_recalcule"]:
            lignes.append(f"    absente du fichier calculé : {c['maille']} {c['code']} {c['periode']}")
    if ecarts["valeurs_differentes"]:
        lignes.append(f"- {len(ecarts['valeurs_differentes'])} valeur(s) différente(s) :")
        for d in ecarts["valeurs_differentes"]:
            lignes.append(
                f"    {d['maille']} {d['code']} {d['periode']} : attendu={d['attendu']} recalcule={d['recalcule']}"
            )
    if not (ecarts["seulement_dans_attendu"] or ecarts["seulement_dans_recalcule"] or ecarts["valeurs_differentes"]):
        lignes.append("Aucun écart.")
    return "\n".join(lignes)


def recalculer(id_indicateur: str) -> int:
    definition = _definition(id_indicateur)
    version = definition["version"]
    module = importlib.import_module(f"verifications.{id_indicateur.replace('.', '_')}")

    attendu = _table_calculee(id_indicateur, version)
    recalcule = _table_recalculee(module)
    ecarts = comparer(attendu, recalcule)
    en_ecart = bool(ecarts["seulement_dans_attendu"] or ecarts["seulement_dans_recalcule"] or ecarts["valeurs_differentes"])

    print(_rapport_texte(id_indicateur, version, ecarts))

    rapport = {
        "date": maintenant(),
        "indicateur": f"{id_indicateur}@{version}",
        "lignes_comparees": ecarts["lignes_comparees"],
        "ecarts": {
            "seulement_dans_attendu": ecarts["seulement_dans_attendu"],
            "seulement_dans_recalcule": ecarts["seulement_dans_recalcule"],
            "valeurs_differentes": ecarts["valeurs_differentes"],
        },
        "statut": "ecart" if en_ecart else "ok",
    }
    ecrire_json(INDICATEURS_CALCULES / f"{id_indicateur}@{version}.recalcul.json", rapport)

    return 1 if en_ecart else 0


def recalculer_tous() -> int:
    """Recalcule chaque indicateur qui a sa vérification ; échoue si un écart apparaît ou si une vérification manque."""
    ids = sorted(d["id"] for _, d in definitions_indicateurs())
    sans_verification = [i for i in ids if importlib.util.find_spec(f"verifications.{i.replace('.', '_')}") is None]
    en_ecart = [i for i in ids if i not in sans_verification and recalculer(i)]
    print(f"\n{len(ids) - len(sans_verification) - len(en_ecart)} indicateurs sans écart, "
          f"{len(en_ecart)} en écart, {len(sans_verification)} sans vérification.")
    for i in en_ecart:
        print(f"ÉCART {i}", file=sys.stderr)
    for i in sans_verification:
        print(f"NON VÉRIFIÉ {i}", file=sys.stderr)
    return 1 if en_ecart or sans_verification else 0


def main() -> int:
    if sys.argv[1:] == ["--tous"]:
        return recalculer_tous()
    if len(sys.argv) != 2:
        print("usage : uv run python -m outils.recalcul <id.indicateur> | --tous", file=sys.stderr)
        return 2
    return recalculer(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
