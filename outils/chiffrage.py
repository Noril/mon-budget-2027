"""Chiffrage des programmes des candidats : contrôle, agrégation, trajectoire de dette, rapport.

    uv run python -m outils.chiffrage            # valide, écrit build/chiffrage.md, build/chiffrage.html, data/chiffrage.json
    uv run python -m outils.chiffrage --valider  # contrôle seulement

Chaque programme (chiffrage/programmes/<id>.yaml) liste des mesures citées verbatim. Chaque mesure chiffrable porte
son effet sur le solde primaire en régime de croisière (Md€ courants 2032, négatif = coût), une fourchette, un
profil de montée en charge et une formule recalculée ici à partir de paramètres, eux-mêmes tirés des barèmes
communs (chiffrage/baremes.yaml) quand ils existent. Les trajectoires de dette réutilisent plan.trajectoire.
"""

from __future__ import annotations

import argparse
from datetime import date
import html
import json
import math
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from pipelines.commun import DONNEES, RACINE, ecrire_json, maintenant
from plan import trajectoire as tr

DOSSIER = RACINE / "chiffrage"
BAREMES = DOSSIER / "baremes.yaml"
PROGRAMMES = DOSSIER / "programmes"
ANNEES = list(range(2027, 2033))
TOLERANCE_MD = 0.05
FONCTIONS = {"min": min, "max": max, "abs": abs, "round": round, "sqrt": math.sqrt}


def _schema(nom: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((RACINE / "schemas" / f"{nom}.schema.json").read_text(encoding="utf-8")))


def _erreurs_schema(v: Draft202012Validator, objet, ou: str) -> list[str]:
    return [f"{ou} : {'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in v.iter_errors(objet)]


def _lire(fichier: Path):
    # les dates YAML deviennent des chaînes, comme le veulent les schémas
    return json.loads(json.dumps(yaml.safe_load(fichier.read_text(encoding="utf-8")), default=str))


def lire_baremes() -> list[dict]:
    return (_lire(BAREMES) or []) if BAREMES.exists() else []


def lire_programmes() -> list[tuple[Path, dict]]:
    return [(f, _lire(f)) for f in sorted(PROGRAMMES.glob("*.yaml"))]


def evaluer(calcul: dict) -> float:
    valeurs = {nom: p["valeur"] for nom, p in calcul["parametres"].items()}
    return float(eval(calcul["formule"], {"__builtins__": {}, **FONCTIONS}, valeurs))  # noqa: S307 (dépôt relu)


def valider() -> list[str]:
    erreurs: list[str] = []
    baremes = lire_baremes()
    schema_b = _schema("bareme")
    ids_b = [b.get("id") for b in baremes]
    for d in sorted({i for i in ids_b if ids_b.count(i) > 1}):
        erreurs.append(f"baremes.yaml : barème « {d} » déclaré plusieurs fois")
    par_id = {}
    for b in baremes:
        erreurs += _erreurs_schema(schema_b, b, f"baremes.yaml:{b.get('id')}")
        par_id[b.get("id")] = b

    schema_p = _schema("programme")
    ids_p = set()
    for fichier, p in lire_programmes():
        ou = str(fichier.relative_to(RACINE))
        erreurs += _erreurs_schema(schema_p, p, ou)
        if p.get("id") != fichier.stem:
            erreurs.append(f"{ou} : id « {p.get('id')} » différent du nom du fichier")
        if p.get("id") in ids_p:
            erreurs.append(f"{ou} : programme en double")
        ids_p.add(p.get("id"))
        ids_m = [m.get("id") for m in p.get("mesures", [])]
        for d in sorted({i for i in ids_m if ids_m.count(i) > 1}):
            erreurs.append(f"{ou} : mesure « {d} » en double")
        for m in p.get("mesures", []):
            if not m.get("chiffrable") or "calcul" not in m or "effet_solde_primaire" not in m:
                continue
            om = f"{ou}:{m['id']}"
            e = m["effet_solde_primaire"]
            for nom, par in m["calcul"]["parametres"].items():
                if (b := par.get("bareme")) is not None:
                    if b not in par_id:
                        erreurs.append(f"{om} : paramètre {nom} renvoie au barème inconnu « {b} »")
                    elif par["valeur"] not in {par_id[b]["valeur"], par_id[b].get("bas"), par_id[b].get("haut")}:
                        erreurs.append(f"{om} : paramètre {nom} = {par['valeur']} ≠ barème {b} ({par_id[b]['valeur']})")
                elif not par.get("source"):
                    erreurs.append(f"{om} : paramètre {nom} sans barème ni source")
            try:
                v = evaluer(m["calcul"])
                if abs(v - e["central"]) > TOLERANCE_MD:
                    erreurs.append(f"{om} : la formule donne {v:.3f}, central = {e['central']}")
            except Exception as exc:  # formule invalide
                erreurs.append(f"{om} : formule non évaluable ({exc})")
            if not e["bas"] <= e["central"] <= e["haut"]:
                erreurs.append(f"{om} : fourchette incohérente (bas ≤ central ≤ haut attendu)")
            if set(map(int, e["montee_en_charge"])) != set(ANNEES):
                erreurs.append(f"{om} : montée en charge à renseigner pour chaque année {ANNEES[0]}-{ANNEES[-1]}")
    return erreurs


# --- Agrégation ---------------------------------------------------------------------------------------


def profil(m: dict, cle: str) -> dict[int, float]:
    e = m["effet_solde_primaire"]
    if "annuel" not in e:
        return {int(a): e[cle] * part for a, part in e["montee_en_charge"].items()}
    annuel = {int(a): v for a, v in e["annuel"].items()}
    return {int(a): annuel.get(int(a), 0.0) + (e[cle] - e["central"]) * part for a, part in e["montee_en_charge"].items()}


def agreger(p: dict) -> dict:
    chiffrees = [m for m in p["mesures"] if m.get("chiffrable") and "effet_solde_primaire" in m]
    totaux = {cle: {a: sum(profil(m, cle).get(a, 0.0) for m in chiffrees) for a in ANNEES} for cle in ("central", "bas", "haut")}
    croisiere = {cle: sum(m["effet_solde_primaire"][cle] for m in chiffrees) for cle in ("central", "bas", "haut")}
    couts = sum(min(m["effet_solde_primaire"]["central"], 0) for m in chiffrees)
    gains = sum(max(m["effet_solde_primaire"]["central"], 0) for m in chiffrees)
    non_chiffrees = [m for m in p["mesures"] if not m.get("chiffrable")]
    sens = {s: sum(1 for m in non_chiffrees if m.get("sens_probable") == s) for s in ("cout", "economie", "neutre", "incertain")}
    indicatives = [m["estimation_indicative"] for m in non_chiffrees if "estimation_indicative" in m]
    budgetaires = len(chiffrees) + sens["cout"] + sens["economie"] + sens["incertain"]
    return {
        "id": p["id"], "candidat": p["candidat"], "parti": p["parti"],
        "sens_non_chiffrees": sens, "couverture": len(chiffrees) / budgetaires if budgetaires else None,
        "indicatif": {c: sum(e[c] for e in indicatives) for c in ("central", "bas", "haut")}, "nb_indicatives": len(indicatives),
        "nb_mesures": len(p["mesures"]), "nb_chiffrees": len(chiffrees),
        "nb_verifiees": sum(1 for m in chiffrees if m.get("verification", {}).get("statut") in ("ok", "corrige")),
        "croisiere": croisiere, "couts": couts, "gains": gains, "par_annee": totaux,
        "annonce": p.get("annonce_candidat"),
        "mesures": [
            {"id": m["id"], "libelle": m["libelle"], "domaine": m["domaine"], "chiffrable": m["chiffrable"],
             "central": m.get("effet_solde_primaire", {}).get("central"), "bas": m.get("effet_solde_primaire", {}).get("bas"),
             "haut": m.get("effet_solde_primaire", {}).get("haut"), "confiance": m.get("confiance"),
             "url": m["citation"]["url"], "verification": m.get("verification", {}).get("statut"),
             "tiers": [(t["auteur"], t.get("montant_md")) for t in m.get("chiffrages_tiers", [])],
             "raison": m.get("raison_non_chiffrable"), "sens": m.get("sens_probable"),
             "indicative": m.get("estimation_indicative"), "citation": m["citation"]["texte"],
             "date": m["citation"].get("date"), "interpretation": m.get("interpretation"),
             "formule": m.get("calcul", {}).get("formule"), "explication": m.get("calcul", {}).get("explication"),
             "parametres": {k: v["valeur"] for k, v in m.get("calcul", {}).get("parametres", {}).items()},
             "effets_retour": m.get("effets_retour"),
             "commentaire_verif": m.get("verification", {}).get("commentaire")}
            for m in p["mesures"]
        ],
    }


def trajectoires(agregats: list[dict]) -> dict:
    doc = yaml.safe_load(tr.HYPOTHESES.read_text(encoding="utf-8"))
    depart = tr.lire_depart()
    sortie = {}
    for variante in (None, "fmi"):
        hyp, _ = tr.hypotheses_par_annee(doc, depart, variante)
        ref = tr.projeter(depart, hyp)
        pib = {l["annee"]: l["pib"] for l in ref}
        cle = variante or "gel"
        sortie[cle] = {"reference": [{k: l[k] for k in ("annee", "dette", "solde")} for l in ref], "programmes": {}}
        for a in agregats:
            sortie[cle]["programmes"][a["id"]] = {}
            for h in ("central", "bas", "haut"):
                ajust = {an: 100 * v / pib[an] for an, v in a["par_annee"][h].items() if an in pib}
                traj = tr.projeter(depart, hyp, ajust)
                sortie[cle]["programmes"][a["id"]][h] = [{k: l[k] for k in ("annee", "dette", "solde")} for l in traj]
        sortie[cle]["depart"] = depart.annee
    return sortie


# --- Rapports -----------------------------------------------------------------------------------------


def _md(x: float | None, signe: bool = True) -> str:
    if x is None:
        return "—"
    return (f"{x:+.1f}" if signe else f"{x:.1f}").replace(".", ",").replace("-", "−")


def rapport_md(agregats: list[dict], traj: dict) -> str:
    l = [
        "# Chiffrage des programmes présidentiels 2027", "",
        f"Généré le {date.today().isoformat()} par `outils.chiffrage`. Effet sur le solde public primaire en Md€ courants "
        "par an en régime de croisière (2032) ; négatif = coût. Fourchette : hypothèse basse et haute. "
        "Aucun effet de second tour n'est compté (voir chiffrage/README.md).", "",
        "| Programme | Mesures chiffrées | Coûts | Économies et recettes | Solde net (fourchette) | Dette 2032 (réf. gel : "
        f"{_md(traj['gel']['reference'][-1]['dette'], False)} % PIB) | Annonce du candidat |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for a in agregats:
        d = traj["gel"]["programmes"][a["id"]]
        ann = a.get("annonce") or {}
        l.append(
            f"| {a['candidat']} ({a['parti']}) | {a['nb_chiffrees']} / {a['nb_mesures']} ({a['nb_verifiees']} vérifiées) | "
            f"{_md(a['couts'])} | {_md(a['gains'])} | {_md(a['croisiere']['central'])} "
            f"[{_md(a['croisiere']['bas'])} ; {_md(a['croisiere']['haut'])}] | "
            f"{_md(d['central'][-1]['dette'], False)} [{_md(d['bas'][-1]['dette'], False)} ; {_md(d['haut'][-1]['dette'], False)}] | "
            f"{ann.get('texte', '—')} |"
        )
    for a in agregats:
        l += ["", f"## {a['candidat']} ({a['parti']})", "", "| Mesure | Domaine | Effet central | Fourchette | Confiance | Tiers | Vérif. |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
        for m in sorted(a["mesures"], key=lambda m: (m["central"] is None, m["central"] or 0)):
            if m["chiffrable"]:
                tiers = "; ".join(f"{t} {_md(v)}" for t, v in m["tiers"]) or "—"
                l.append(f"| [{m['libelle']}]({m['url']}) | {m['domaine']} | {_md(m['central'])} | "
                         f"[{_md(m['bas'])} ; {_md(m['haut'])}] | {m['confiance']} | {tiers} | {m['verification'] or '—'} |")
            else:
                l.append(f"| [{m['libelle']}]({m['url']}) | {m['domaine']} | non chiffrable | {m['raison']} | | | |")
    return "\n".join(l) + "\n"


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{round(100 * x)} %"


def _svg_dette(traj: dict, agregats: list[dict]) -> str:
    couleurs = ["#c0392b", "#8e44ad", "#2471a3", "#17a589", "#d4ac0d", "#ca6f1e", "#566573", "#1f618d", "#943126", "#1e8449"]
    ref = traj["reference"]
    series = [(a["candidat"], traj["programmes"][a["id"]]["central"]) for a in agregats]
    toutes = [p["dette"] for _, s in series for p in s] + [p["dette"] for p in ref]
    ymin, ymax = math.floor(min(toutes) / 5) * 5, math.ceil(max(toutes) / 5) * 5
    L, H, g, d, h, b = 760, 380, 50, 170, 20, 30
    annees = [p["annee"] for p in ref]
    x = lambda an: g + (an - annees[0]) / (annees[-1] - annees[0]) * (L - g - d)
    y = lambda v: h + (ymax - v) / (ymax - ymin) * (H - h - b)
    parts = [f'<svg viewBox="0 0 {L} {H}" role="img" aria-label="Dette publique projetée">']
    for v in range(ymin, ymax + 1, 5):
        parts.append(f'<line x1="{g}" x2="{L - d}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grille"/>'
                     f'<text x="{g - 6}" y="{y(v) + 4:.1f}" text-anchor="end" class="axe">{v}</text>')
    for an in annees:
        parts.append(f'<text x="{x(an):.1f}" y="{H - 8}" text-anchor="middle" class="axe">{an}</text>')
    etiquettes = []
    for i, (nom, s) in enumerate([("Référence (solde gelé)", ref)] + series):
        c = "var(--muted)" if i == 0 else couleurs[(i - 1) % len(couleurs)]
        pts = " ".join(f"{x(p['annee']):.1f},{y(p['dette']):.1f}" for p in s)
        tiret = ' stroke-dasharray="5 4"' if i == 0 else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2"{tiret}/>')
        etiquettes.append((y(s[-1]["dette"]), c, f"{nom} {_md(s[-1]['dette'], False)}"))
    etiquettes.sort()
    dernier = -99.0
    for yy, c, t in etiquettes:
        yy = max(yy, dernier + 13)
        dernier = yy
        parts.append(f'<text x="{L - d + 6}" y="{yy + 4:.1f}" fill="{c}" class="leg">{html.escape(t)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _detail(m: dict) -> str:
    e = html.escape
    parts = [f"<blockquote>« {e(m['citation'])} »{' (' + e(str(m['date'])) + ')' if m.get('date') else ''}</blockquote>"]
    for titre, cle in (("Lecture retenue", "interpretation"), ("Calcul", "explication"), ("Non compté", "effets_retour"),
                       ("Vérification", "commentaire_verif")):
        if m.get(cle):
            parts.append(f"<p><b>{titre}.</b> {e(str(m[cle]))}</p>")
    if m.get("formule"):
        params = ", ".join(f"{e(k)} = {v:g}" for k, v in m["parametres"].items())
        parts.append(f"<p><code>{e(m['formule'])}</code><br><small>{params}</small></p>")
    return "<details><summary>détail</summary>" + "".join(parts) + "</details>"


def _svg_soldes(agregats: list[dict]) -> str:
    """Solde net en régime de croisière, point central et fourchette, un programme par ligne."""
    rangs = sorted(agregats, key=lambda a: a["croisiere"]["central"], reverse=True)
    vals = [v for a in rangs for v in a["croisiere"].values()] + [0]
    vmin, vmax = math.floor(min(vals) / 50) * 50, math.ceil(max(vals) / 50) * 50
    L, g, d, h, pas = 760, 210, 20, 30, 34
    H = h + pas * len(rangs) + 10
    x = lambda v: g + (v - vmin) / (vmax - vmin) * (L - g - d)
    parts = [f'<svg viewBox="0 0 {L} {H}" role="img" aria-label="Solde net par programme">']
    for v in range(vmin, vmax + 1, 50):
        parts.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{h - 8}" y2="{H - 6}" class="grille"/>'
                     f'<text x="{x(v):.1f}" y="{h - 12}" text-anchor="middle" class="axe">{v if v == 0 else f'{v:+d}'}</text>')
    parts.append(f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="{h - 8}" y2="{H - 6}" stroke="var(--fg)" stroke-width="1"/>')
    for i, a in enumerate(rangs):
        y = h + pas * i + pas / 2
        c = a["croisiere"]
        coul = "var(--neg)" if c["central"] < 0 else "var(--pos)"
        parts.append(
            f'<text x="{g - 8}" y="{y + 4:.1f}" text-anchor="end" class="leg">{html.escape(a["candidat"])}</text>'
            f'<line x1="{x(c["bas"]):.1f}" x2="{x(c["haut"]):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{coul}" stroke-opacity=".35" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="{x(c["central"]):.1f}" cy="{y:.1f}" r="6" fill="{coul}"/>'
            f'<text x="{x(c["central"]):.1f}" y="{y - 9:.1f}" text-anchor="middle" class="leg">{_md(c["central"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def rapport_html(agregats: list[dict], traj: dict) -> str:
    e = html.escape
    lignes = []
    for a in sorted(agregats, key=lambda a: a["croisiere"]["central"], reverse=True):
        dg = traj["gel"]["programmes"][a["id"]]
        lignes.append(
            f"<tr><td><a href='#{a['id']}'>{e(a['candidat'])}</a><br><small>{e(a['parti'])}</small></td>"
            f"<td>{a['nb_chiffrees']} / {a['nb_mesures']}<br><small>{a['nb_verifiees']} vérifiées</small></td>"
            f"<td class='n neg'>{_md(a['couts'])}</td><td class='n pos'>{_md(a['gains'])}</td>"
            f"<td class='n'><b>{_md(a['croisiere']['central'])}</b><br><small>[{_md(a['croisiere']['bas'])} ; {_md(a['croisiere']['haut'])}]</small></td>"
            f"<td class='n'>{_md(a['indicatif']['central']) if a['nb_indicatives'] else '—'}<br><small>{a['nb_indicatives']} mesures ; "
            f"coût probable {a['sens_non_chiffrees']['cout']}, économie {a['sens_non_chiffrees']['economie']}, "
            f"incertain {a['sens_non_chiffrees']['incertain']}</small></td>"
            f"<td class='n'>{_pct(a['couverture'])}</td>"
            f"<td class='n'><b>{_md(dg['central'][-1]['dette'], False)}</b><br><small>[{_md(dg['bas'][-1]['dette'], False)} ; {_md(dg['haut'][-1]['dette'], False)}]</small></td></tr>"
        )
    sections = []
    for a in agregats:
        rows = []
        for m in sorted(a["mesures"], key=lambda m: (m["central"] is None, m["central"] or 0)):
            lien = f"<a href='{e(m['url'])}'>{e(m['libelle'])}</a>" + _detail(m)
            if m["chiffrable"]:
                tiers = "<br>".join(f"{e(t)} : {_md(v)}" for t, v in m["tiers"]) or "—"
                cls = "neg" if (m["central"] or 0) < 0 else "pos"
                rows.append(f"<tr><td>{lien}</td><td>{e(m['domaine'])}</td><td class='n {cls}'>{_md(m['central'])}</td>"
                            f"<td class='n'><small>[{_md(m['bas'])} ; {_md(m['haut'])}]</small></td><td>{e(m['confiance'] or '')}</td>"
                            f"<td><small>{tiers}</small></td><td>{e(m['verification'] or '—')}</td></tr>")
            else:
                rows.append(f"<tr class='nc'><td>{lien}</td><td>{e(m['domaine'])}</td><td colspan='5'><small>Non chiffrable : {e(m['raison'] or '')}"
                            f"{' — sens probable : ' + e(m['sens']) if m.get('sens') else ''}"
                            f"{' — ordre de grandeur indicatif : ' + _md(m['indicative']['central']) + ' [' + _md(m['indicative']['bas']) + ' ; ' + _md(m['indicative']['haut']) + '] (' + e(m['indicative']['lecture']) + ')' if m.get('indicative') else ''}"
                            "</small></td></tr>")
        sections.append(
            f"<section id='{a['id']}'><h2>{e(a['candidat'])} <small>{e(a['parti'])}</small></h2>"
            f"<p class='m'><b>Ce que dit le candidat.</b> {e((a.get('annonce') or {}).get('texte', 'Aucun chiffrage global publié.'))}</p>"
            "<div class='scroll'><table><thead><tr><th>Mesure</th><th>Domaine</th><th>Effet central</th><th>Fourchette</th>"
            "<th>Confiance</th><th>Chiffrages tiers</th><th>Vérif.</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div></section>"
        )
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chiffrage des programmes 2027</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#77756f;--line:#e2dfd7;--neg:#b03a2e;--pos:#1e7a4a;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--fg:#ecebe6;--muted:#9a978f;--line:#34332f;--neg:#e0796e;--pos:#6fcf97;--card:#1f1f1c}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 64px}}h1{{font-size:1.7rem;margin:.2em 0}}h2{{margin-top:2.2em}}
h2 small{{color:var(--muted);font-weight:400;font-size:.7em}}a{{color:inherit}}p.m{{color:var(--muted);max-width:75ch}}
table{{border-collapse:collapse;width:100%;background:var(--card)}}th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
th{{font-size:.8rem;color:var(--muted);font-weight:600}}.n{{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}}
.neg{{color:var(--neg)}}.pos{{color:var(--pos)}}tr.nc td{{color:var(--muted)}}small{{color:var(--muted)}}
.scroll{{overflow-x:auto}}details{{margin-top:4px}}summary{{cursor:pointer;color:var(--muted);font-size:.8rem}}
details p,blockquote{{font-size:.85rem;max-width:70ch;margin:.4em 0}}blockquote{{border-left:3px solid var(--line);padding-left:8px;color:var(--muted)}}
code{{font-size:.8rem;word-break:break-all}}svg{{width:100%;height:auto;background:var(--card)}}.grille{{stroke:var(--line)}}.axe{{fill:var(--muted);font-size:11px}}.leg{{font-size:11px}}
</style></head><body><main>
<h1>Chiffrage des programmes présidentiels 2027</h1>
<p class="m">Généré le {date.today().isoformat()}. Effet sur le solde public primaire, en milliards d'euros courants par an en régime de
croisière (2032) ; négatif = coût pour les finances publiques. Chaque mesure est citée verbatim avec son lien, calculée par
une formule rejouable à partir de barèmes publics, et confrontée aux chiffrages tiers quand ils existent. Aucun effet de
second tour (croissance, emploi, taux) n'est compté. Trajectoires : modèle du dépôt (plan/trajectoire.py), hypothèses
macroéconomiques du FMI, solde primaire de référence gelé au dernier niveau observé ({traj['gel']['depart']}).</p>
<h2>Solde net par an en 2032 (Md€, point central et fourchette)</h2>{_svg_soldes(agregats)}
<p class="m">À lire avant de comparer : les programmes ne sont pas publiés au même degré de détail. La colonne « Mesures
chiffrées » dit combien de mesures ont un effet budgétaire estimable ; une enveloppe d'économies globale sans mesure
identifiée compte zéro au central et n'apparaît que dans le haut de la fourchette. Les programmes évoluent jusqu'au
dépôt des candidatures : chaque fiche porte sa date de collecte.</p>
<div class="scroll"><table><thead><tr><th>Programme</th><th>Mesures chiffrées</th><th>Coûts</th><th>Économies, recettes</th>
<th>Solde net / an</th><th>Non chiffré : estimation indicative</th><th>Couverture</th><th>Dette 2032, % PIB (réf. {_md(traj['gel']['reference'][-1]['dette'], False)})</th></tr></thead>
<tbody>{''.join(lignes)}</tbody></table></div>
<h2>Dette publique projetée, scénario central (% du PIB)</h2>{_svg_dette(traj['gel'], agregats)}
{''.join(sections)}
</main></body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--valider", action="store_true")
    args = parser.parse_args(argv)
    erreurs = valider()
    for err in erreurs:
        print(f"ÉCHEC {err}", file=sys.stderr)
    if erreurs or args.valider:
        print(f"{len(erreurs)} erreur(s).")
        return 1 if erreurs else 0
    agregats = [agreger(p) for _, p in lire_programmes()]
    traj = trajectoires(agregats)
    build = RACINE / "build"
    build.mkdir(exist_ok=True)
    (build / "chiffrage.md").write_text(rapport_md(agregats, traj), encoding="utf-8")
    (build / "chiffrage.html").write_text(rapport_html(agregats, traj), encoding="utf-8")
    ecrire_json(DONNEES / "chiffrage.json", {"programmes": agregats, "trajectoires": traj})
    for a in agregats:
        print(f"  {a['id']:<20} {a['nb_chiffrees']:>3}/{a['nb_mesures']:<3} solde net {a['croisiere']['central']:+.1f} Md€/an")
    print("-> build/chiffrage.md, build/chiffrage.html, data/chiffrage.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
