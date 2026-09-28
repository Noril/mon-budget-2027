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
    return {
        "id": p["id"], "candidat": p["candidat"], "parti": p["parti"],
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
             "raison": m.get("raison_non_chiffrable")}
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
        f"Généré le {maintenant()[:10]} par `outils.chiffrage`. Effet sur le solde public primaire en Md€ courants "
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


def rapport_html(agregats: list[dict], traj: dict) -> str:
    e = html.escape
    lignes = []
    for a in agregats:
        dg = traj["gel"]["programmes"][a["id"]]
        ann = (a.get("annonce") or {}).get("texte", "—")
        lignes.append(
            f"<tr><td><a href='#{a['id']}'>{e(a['candidat'])}</a><br><small>{e(a['parti'])}</small></td>"
            f"<td>{a['nb_chiffrees']} / {a['nb_mesures']}<br><small>{a['nb_verifiees']} vérifiées</small></td>"
            f"<td class='n neg'>{_md(a['couts'])}</td><td class='n pos'>{_md(a['gains'])}</td>"
            f"<td class='n'><b>{_md(a['croisiere']['central'])}</b><br><small>[{_md(a['croisiere']['bas'])} ; {_md(a['croisiere']['haut'])}]</small></td>"
            f"<td class='n'><b>{_md(dg['central'][-1]['dette'], False)}</b><br><small>[{_md(dg['bas'][-1]['dette'], False)} ; {_md(dg['haut'][-1]['dette'], False)}]</small></td>"
            f"<td><small>{e(ann)}</small></td></tr>"
        )
    sections = []
    for a in agregats:
        rows = []
        for m in sorted(a["mesures"], key=lambda m: (m["central"] is None, m["central"] or 0)):
            lien = f"<a href='{e(m['url'])}'>{e(m['libelle'])}</a>"
            if m["chiffrable"]:
                tiers = "<br>".join(f"{e(t)} : {_md(v)}" for t, v in m["tiers"]) or "—"
                cls = "neg" if (m["central"] or 0) < 0 else "pos"
                rows.append(f"<tr><td>{lien}</td><td>{e(m['domaine'])}</td><td class='n {cls}'>{_md(m['central'])}</td>"
                            f"<td class='n'><small>[{_md(m['bas'])} ; {_md(m['haut'])}]</small></td><td>{e(m['confiance'] or '')}</td>"
                            f"<td><small>{tiers}</small></td><td>{e(m['verification'] or '—')}</td></tr>")
            else:
                rows.append(f"<tr class='nc'><td>{lien}</td><td>{e(m['domaine'])}</td><td colspan='5'><small>Non chiffrable : {e(m['raison'] or '')}</small></td></tr>")
        sections.append(
            f"<section id='{a['id']}'><h2>{e(a['candidat'])} <small>{e(a['parti'])}</small></h2>"
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
.scroll{{overflow-x:auto}}svg{{width:100%;height:auto;background:var(--card)}}.grille{{stroke:var(--line)}}.axe{{fill:var(--muted);font-size:11px}}.leg{{font-size:11px}}
</style></head><body><main>
<h1>Chiffrage des programmes présidentiels 2027</h1>
<p class="m">Généré le {maintenant()[:10]}. Effet sur le solde public primaire, en milliards d'euros courants par an en régime de
croisière (2032) ; négatif = coût pour les finances publiques. Chaque mesure est citée verbatim avec son lien, calculée par
une formule rejouable à partir de barèmes publics, et confrontée aux chiffrages tiers quand ils existent. Aucun effet de
second tour (croissance, emploi, taux) n'est compté. Trajectoires : modèle du dépôt (plan/trajectoire.py), hypothèses
macroéconomiques du FMI, solde primaire de référence gelé au dernier niveau observé ({traj['gel']['depart']}).</p>
<div class="scroll"><table><thead><tr><th>Programme</th><th>Mesures chiffrées</th><th>Coûts</th><th>Économies, recettes</th>
<th>Solde net / an</th><th>Dette 2032, % PIB (réf. {_md(traj['gel']['reference'][-1]['dette'], False)})</th><th>Annonce du candidat</th></tr></thead>
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
