"""Compte de la France : dynamique de la dette publique, trajectoire de référence et scénarios.

    uv run python -m plan.trajectoire                               # référence (solde primaire gelé)
    uv run python -m plan.trajectoire --variante fmi                # solde primaire des projections du FMI
    uv run python -m plan.trajectoire --scenario plan/scenarios/exemple.yaml

Modèle (ratios en points de PIB, taux en fraction) :
    g_nominale(t)       = (1 + croissance(t)) × (1 + inflation(t)) − 1
    charge_interets(t)  = taux(t) × dette(t−1) / (1 + g_nominale(t))
    dette(t)            = dette(t−1) × (1 + taux(t)) / (1 + g_nominale(t)) − solde_primaire(t)
    solde(t)            = solde_primaire(t) − charge_interets(t)
Point de départ : dernière année observée commune aux indicateurs finances.* (maille france).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import duckdb
import yaml

from pipelines.commun import (
    DONNEES,
    INDICATEURS_CALCULES,
    NORMALISE,
    RACINE,
    definitions_indicateurs,
    ecrire_json,
    lire_json,
    maintenant,
    sha256,
)

HYPOTHESES = RACINE / "plan" / "hypotheses.yaml"
SORTIES = DONNEES / "plan"
VARIABLES = ("croissance", "inflation", "taux", "solde_primaire")
COLONNES = ["annee", "croissance", "inflation", "taux", "solde_primaire", "solde", "dette", "charge_interets", "pib"]
TOLERANCE = 6e-4  # valeurs du YAML arrondies à 0,001


class HypotheseInvalide(Exception):
    pass


@dataclass
class Depart:
    annee: int
    dette: float  # % du PIB, fin d'année
    solde: float  # % du PIB
    charge_interets: float  # % du PIB
    pib: float  # Md€ courants

    @property
    def solde_primaire(self) -> float:
        return self.solde + self.charge_interets


# --- Modèle ------------------------------------------------------------------------------------------


def projeter(depart: Depart, hypotheses: dict[int, dict[str, float]], ajustements: dict[int, float] | None = None) -> list[dict]:
    """Projette la dette année par année. `hypotheses[annee]` : croissance, inflation, taux en %, solde_primaire en
    points de PIB. `ajustements[annee]` : points de PIB ajoutés au solde primaire (négatif = coût des mesures)."""
    ajustements = ajustements or {}
    if inconnues := set(ajustements) - set(hypotheses):
        raise HypotheseInvalide(f"ajustements hors horizon : {sorted(inconnues)}")
    lignes = [
        {
            "annee": depart.annee, "croissance": None, "inflation": None, "taux": None,
            "solde_primaire": depart.solde_primaire, "solde": depart.solde, "dette": depart.dette,
            "charge_interets": depart.charge_interets, "pib": depart.pib,
        }
    ]
    dette, pib = depart.dette, depart.pib
    for annee in sorted(hypotheses):
        if annee != lignes[-1]["annee"] + 1:
            raise HypotheseInvalide(f"année {annee} : les hypothèses doivent suivre {lignes[-1]['annee']} sans trou")
        h = hypotheses[annee]
        g_nominale = (1 + h["croissance"] / 100) * (1 + h["inflation"] / 100) - 1
        taux = h["taux"] / 100
        solde_primaire = h["solde_primaire"] + ajustements.get(annee, 0.0)
        charge = taux * dette / (1 + g_nominale)
        dette = dette * (1 + taux) / (1 + g_nominale) - solde_primaire
        pib = pib * (1 + g_nominale)
        lignes.append(
            {
                "annee": annee, "croissance": h["croissance"], "inflation": h["inflation"], "taux": h["taux"],
                "solde_primaire": solde_primaire, "solde": solde_primaire - charge, "dette": dette,
                "charge_interets": charge, "pib": pib,
            }
        )
    return lignes


def ajustements_scenario(scenario: dict, pib: dict[int, float]) -> dict[int, float]:
    """Somme, par année, des effets des mesures sur le solde primaire, en points de PIB.
    Unité `md_eur` : milliards d'euros courants, convertis avec le PIB nominal de la trajectoire de référence."""
    total: dict[int, float] = {}
    for mesure in scenario.get("mesures", []):
        effet = mesure["effet_solde_primaire"]
        for annee, valeur in effet["valeurs"].items():
            annee = int(annee)
            if effet["unite"] == "pts_pib":
                points = float(valeur)
            elif effet["unite"] == "md_eur":
                if annee not in pib:
                    raise HypotheseInvalide(f"{mesure['id']} : année {annee} hors trajectoire")
                points = 100 * float(valeur) / pib[annee]
            else:
                raise HypotheseInvalide(f"{mesure['id']} : unité « {effet['unite']} », attendu md_eur ou pts_pib")
            total[annee] = total.get(annee, 0.0) + points
    return total


# --- Lecture des données et des hypothèses ------------------------------------------------------------


def _serie_indicateur(id_indicateur: str) -> dict[int, float]:
    versions = {d["id"]: d["version"] for _, d in definitions_indicateurs()}
    table = INDICATEURS_CALCULES / f"{id_indicateur}@{versions[id_indicateur]}.parquet"
    if not table.exists():
        raise HypotheseInvalide(f"{table.name} absent : lancer `uv run python -m pipelines.indicateurs`")
    lignes = duckdb.execute(
        f"SELECT periode, valeur FROM read_parquet('{table}') WHERE maille = 'france' AND code = 'FR'"
    ).fetchall()
    return {int(p): v for p, v in lignes}


INDICATEURS_DEPART = {
    "dette": "finances.dette_publique",
    "solde": "finances.solde_public",
    "charge_interets": "finances.charge_interets",
    "pib": "finances.pib_nominal",
}


def lire_depart() -> Depart:
    series = {cle: _serie_indicateur(i) for cle, i in INDICATEURS_DEPART.items()}
    communes = set.intersection(*(set(s) for s in series.values()))
    if not communes:
        raise HypotheseInvalide("aucune année commune aux indicateurs de départ")
    annee = max(communes)
    return Depart(annee=annee, **{cle: s[annee] for cle, s in series.items()})


def _series_fmi() -> dict[str, dict[int, float]]:
    table = NORMALISE / "fmi-weo.parquet"
    if not table.exists():
        raise HypotheseInvalide("fmi-weo absent de la zone normalisée : `uv run python -m pipelines.ingest fmi-weo`")
    series: dict[str, dict[int, float]] = {}
    for indicateur, periode, valeur in duckdb.execute(
        f"SELECT INDICATOR, TIME_PERIOD, CAST(OBS_VALUE AS DOUBLE) FROM read_parquet('{table}') WHERE OBS_VALUE IS NOT NULL"
    ).fetchall():
        series.setdefault(indicateur, {})[int(periode)] = valeur
    return series


def _recalculer(derivation: dict, annee: int, fmi: dict[str, dict[int, float]], valeurs: dict[str, dict[int, float]]) -> float | None:
    """Valeur attendue d'après la source ; None si la dérivation ne se vérifie pas dans une source."""
    match derivation["type"]:
        case "serie":
            return fmi[derivation["serie"]][annee]
        case "variation":
            s = fmi[derivation["serie"]]
            return 100 * (s[annee] / s[annee - 1] - 1)
        case "taux_implicite":
            interets_nets = fmi["GGXONLB_NGDP"][annee] - fmi["GGXCNL_NGDP"][annee]
            return 100 * interets_nets * fmi["NGDP"][annee] / (fmi["GGXWDG_NGDP"][annee - 1] * fmi["NGDP"][annee - 1])
        case "reconduction":
            return valeurs[derivation["hypothese"]][derivation["annee"]]
        case _:
            return None


def verifier(doc: dict, fmi: dict[str, dict[int, float]]) -> list[str]:
    """Contrôle chaque valeur du YAML contre sa source ; renvoie les écarts."""
    erreurs = []
    valeurs = {h["id"]: h.get("valeurs", {}) for h in doc["hypotheses"]}
    blocs = [(h["id"], h) for h in doc["hypotheses"]]
    blocs += [(f"{h['id']}.{h['variante_sourcee']['id']}", h["variante_sourcee"]) for h in doc["hypotheses"] if "variante_sourcee" in h]
    for nom, h in blocs:
        if not h.get("a_trancher") and not h.get("url"):
            erreurs.append(f"{nom} : ni source (url) ni a_trancher")
        for annee, valeur in h.get("valeurs", {}).items():
            try:
                attendu = _recalculer(h["derivation"], int(annee), fmi, valeurs)
            except KeyError as e:
                erreurs.append(f"{nom} {annee} : série ou année absente de la source ({e})")
                continue
            if attendu is not None and abs(attendu - valeur) > TOLERANCE:
                erreurs.append(f"{nom} {annee} : {valeur} dans le YAML, {attendu:.4f} dans la source (nouveau millésime ?)")
        if (p := h.get("prolongement_2032")) and p["valeur"] != h["valeurs"][max(h["valeurs"])]:
            erreurs.append(f"{nom} : le prolongement 2032 doit reconduire la dernière valeur sourcée")
    return erreurs


def hypotheses_par_annee(doc: dict, depart: Depart, variante: str | None = None) -> tuple[dict[int, dict[str, float]], list[str]]:
    """Assemble les hypothèses par année ; renvoie aussi la liste des hypothèses `a_trancher` utilisées."""
    annees = [int(a) for a in doc["annees"]]
    table: dict[int, dict[str, float]] = {a: {} for a in annees}
    a_trancher = []
    for h in doc["hypotheses"]:
        var = h["variable"]
        if var == "solde_primaire":
            if variante is not None and variante == h.get("variante_sourcee", {}).get("id"):
                v = h["variante_sourcee"]
                serie = {int(a): x for a, x in v["valeurs"].items()}
                prolongement = v.get("prolongement_2032")
                if prolongement:
                    serie[2032] = prolongement["valeur"]
                    a_trancher.append(f"{h['id']}.{v['id']} 2032 : {prolongement['convention']}")
            elif variante is None and h["derivation"]["type"] == "gel_observe":
                serie = {a: depart.solde_primaire for a in annees}
                a_trancher.append(f"{h['id']} : {' '.join(h['convention'].split())}")
            else:
                raise HypotheseInvalide(f"variante « {variante} » inconnue pour {h['id']}")
        else:
            serie = {int(a): x for a, x in h["valeurs"].items()}
            if h.get("a_trancher"):
                a_trancher.append(f"{h['id']} : {h['convention']}")
        for a, x in serie.items():
            if a in table:
                if var in table[a]:
                    raise HypotheseInvalide(f"{var} {a} défini deux fois")
                table[a][var] = x
    for a, vals in table.items():
        if manquantes := set(VARIABLES) - set(vals):
            raise HypotheseInvalide(f"{a} : hypothèses manquantes {sorted(manquantes)}")
    return table, a_trancher


# --- Sorties ------------------------------------------------------------------------------------------


def ecrire_parquet(lignes: list[dict], sortie: Path) -> None:
    sortie.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (annee INTEGER, croissance DOUBLE, inflation DOUBLE, taux DOUBLE, solde_primaire DOUBLE, "
        "solde DOUBLE, dette DOUBLE, charge_interets DOUBLE, pib DOUBLE, nature VARCHAR)"
    )
    con.executemany(
        "INSERT INTO t VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [[l[c] for c in COLONNES] + ["observe" if i == 0 else "projete"] for i, l in enumerate(lignes)],
    )
    con.execute(f"COPY t TO '{sortie}' (FORMAT parquet)")


def _f(x: float | None, n: int = 1) -> str:
    return "" if x is None else f"{x:.{n}f}"


def resume(lignes: list[dict]) -> str:
    entete = f"{'année':>5} {'croiss.':>7} {'défl.':>6} {'taux':>6} {'s.prim.':>7} {'solde':>6} {'intérêts':>8} {'dette':>6}"
    corps = [
        f"{l['annee']:>5} {_f(l['croissance'], 2):>7} {_f(l['inflation'], 2):>6} {_f(l['taux'], 2):>6} "
        f"{_f(l['solde_primaire']):>7} {_f(l['solde']):>6} {_f(l['charge_interets'], 2):>8} {_f(l['dette']):>6}"
        for l in lignes
    ]
    return "\n".join([entete, *corps])


def ecart(reference: list[dict], scenario: list[dict]) -> str:
    lignes = [f"{'année':>5} {'Δ s.prim.':>9} {'Δ solde':>8} {'Δ dette':>8}   (points de PIB, scénario − référence)"]
    for r, s in zip(reference[1:], scenario[1:]):
        lignes.append(
            f"{r['annee']:>5} {s['solde_primaire'] - r['solde_primaire']:>+9.2f} {s['solde'] - r['solde']:>+8.2f} "
            f"{s['dette'] - r['dette']:>+8.2f}"
        )
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variante", help="variante sourcée du solde primaire (ex. fmi) ; défaut : gel au dernier observé")
    parser.add_argument("--scenario", type=Path, help="YAML des effets des mesures sur le solde primaire")
    args = parser.parse_args(argv)

    try:
        doc = yaml.safe_load(HYPOTHESES.read_text(encoding="utf-8"))
        if erreurs := verifier(doc, _series_fmi()):
            for e in erreurs:
                print(f"ÉCHEC hypothèse {e}", file=sys.stderr)
            return 1
        depart = lire_depart()
        hypotheses, a_trancher = hypotheses_par_annee(doc, depart, args.variante)
        reference = projeter(depart, hypotheses)
    except HypotheseInvalide as e:
        print(f"ÉCHEC {e}", file=sys.stderr)
        return 1

    nom = "trajectoire_reference" + (f"_{args.variante}" if args.variante else "")
    ecrire_parquet(reference, SORTIES / f"{nom}.parquet")
    lignage = {
        "calcule_le": maintenant(),
        "hypotheses": str(HYPOTHESES.relative_to(RACINE)),
        "hypotheses_sha256": sha256(HYPOTHESES),
        "variante_solde_primaire": args.variante or "gel_observe",
        "depart": depart.__dict__ | {"indicateurs": INDICATEURS_DEPART},
        "sources_fmi": lire_json(NORMALISE / "fmi-weo.manifeste.json")["fichiers"],
        "a_trancher": a_trancher,
    }
    ecrire_json(SORTIES / f"{nom}.lignage.json", lignage)

    print(f"Compte de la France, {doc['millesime']} ; départ {depart.annee} observé.")
    print(resume(reference))
    print("Hypothèses à trancher :")
    for a in a_trancher:
        print(f"  - {a}")
    print(f"-> {(SORTIES / f'{nom}.parquet').relative_to(RACINE)}")

    if args.scenario:
        scenario = yaml.safe_load(args.scenario.read_text(encoding="utf-8"))
        try:
            ajust = ajustements_scenario(scenario, {l["annee"]: l["pib"] for l in reference})
            variante = projeter(depart, hypotheses, ajust)
        except HypotheseInvalide as e:
            print(f"ÉCHEC scénario {e}", file=sys.stderr)
            return 1
        sortie = SORTIES / f"trajectoire_{scenario['id']}.parquet"
        ecrire_parquet(variante, sortie)
        print(f"\nScénario « {scenario['id']} » : {scenario.get('libelle', '')}")
        print(ecart(reference, variante))
        print(f"-> {sortie.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
