"""Simulateur budgétaire : composer son budget 2027-2032 levier par levier et se situer parmi les candidats.

    uv run python -m outils.simulateur             # valide chiffrage/simulateur.yaml, écrit build/simulateur.html
    uv run python -m outils.simulateur --valider

Les leviers (chiffrage/simulateur.yaml) reprennent les chiffrages des programmes et les barèmes communs. La page est
autonome (HTML, CSS et JS en ligne, données embarquées) : la trajectoire de dette est recalculée dans le navigateur
avec la même équation que plan/trajectoire.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date

import yaml
from jsonschema import Draft202012Validator

from pipelines.commun import RACINE
from plan import trajectoire as tr

from .chiffrage import ANNEES, agreger, lire_programmes

LEVIERS = RACINE / "chiffrage" / "simulateur.yaml"
SORTIE = RACINE / "build" / "simulateur.html"
COULEURS = ["#c0392b", "#8e44ad", "#2471a3", "#17a589", "#b7950b", "#ca6f1e", "#566573", "#943126", "#1e8449", "#1f618d"]
TOLERANCE_REPRISE = 0.05  # Md€
GLOSSAIRE = RACINE / "chiffrage" / "glossaire.yaml"
# Axes de comparaison thématiques : des directions descriptives, jamais un jugement.
AXES = {
    "protection-sociale": ("Protection sociale", "prestations et retraites moins généreuses", "plus généreuses"),
    "imposition-hauts-revenus-patrimoine": ("Impôts sur les hauts revenus et le patrimoine", "moins", "plus"),
    "soutien-entreprises": ("Soutien aux entreprises", "moins d'aides et d'allègements", "plus"),
    "services-agents-publics": ("Services et agents publics", "moins", "plus"),
    "conditions-etrangers": ("Accès des étrangers aux prestations", "plus ouvert", "plus restreint"),
    "transition-ecologique": ("Transition écologique", "moins d'effort", "plus d'effort"),
    "defense": ("Défense", "moins de dépenses", "plus de dépenses"),
    "ouverture-internationale": ("Aide au développement et Europe", "moins", "plus"),
}


def json_pour_script(objet) -> str:
    """JSON à embarquer dans un <script> : `<`, `>` et `&` échappés (un « </script> » dans une donnée ne referme pas la balise)."""
    return json.dumps(objet, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def remplir(page: str, **valeurs: str) -> str:
    """Remplace les marqueurs __NOM__ en un seul passage : une valeur insérée n'est jamais réinterprétée."""
    return re.sub(r"__([A-Z_]+)__", lambda m: valeurs.get(m.group(1), m.group(0)), page)


def lire_leviers() -> dict:
    return json.loads(json.dumps(yaml.safe_load(LEVIERS.read_text(encoding="utf-8")), default=str))


def valider(doc: dict | None = None) -> list[str]:
    if not LEVIERS.exists():
        return []
    doc = doc or lire_leviers()
    schema = Draft202012Validator(json.loads((RACINE / "schemas" / "simulateur.schema.json").read_text(encoding="utf-8")))
    erreurs = [f"simulateur.yaml : {'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in schema.iter_errors(doc)]
    if erreurs:
        return erreurs
    programmes = {p["id"]: {m["id"]: m for m in p["mesures"]} for _, p in lire_programmes()}
    ids = [l["id"] for l in doc["leviers"]]
    erreurs += [f"simulateur.yaml : levier « {i} » en double" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for l in doc["leviers"]:
        ou = f"simulateur.yaml:{l['id']}"
        if l["type"] == "choix":
            opts = l.get("options", [])
            if len(opts) < 2:
                erreurs.append(f"{ou} : un levier « choix » demande au moins deux options")
            if sum(bool(o.get("defaut")) for o in opts) != 1:
                erreurs.append(f"{ou} : une et une seule option par défaut (droit constant)")
            for o in opts:
                e = o["effet"]
                if o.get("defaut") and any(e.values()):
                    erreurs.append(f"{ou}/{o['id']} : l'option par défaut (droit constant) doit avoir un effet nul")
                if not e["bas"] <= e["central"] <= e["haut"]:
                    erreurs.append(f"{ou}/{o['id']} : fourchette incohérente (bas ≤ central ≤ haut)")
                for c in o.get("candidats", []):
                    if c not in programmes:
                        erreurs.append(f"{ou}/{o['id']} : programme inconnu « {c} »")
                for r in o.get("reprend", []):
                    prog, _, mes = r.partition("/")
                    if mes not in programmes.get(prog, {}):
                        erreurs.append(f"{ou}/{o['id']} : mesure reprise introuvable « {r} »")
            for c in programmes:
                if sum(c in o.get("candidats", []) for o in opts) > 1:
                    erreurs.append(f"{ou} : « {c} » associé à plusieurs options")
        else:
            cur = l.get("curseur")
            if not cur:
                erreurs.append(f"{ou} : un levier « curseur » demande un bloc curseur")
                continue
            if not cur["min"] <= 0 <= cur["max"]:
                erreurs.append(f"{ou} : le curseur doit contenir 0 (droit constant)")
            for c, v in cur.get("positions", {}).items():
                if c not in programmes:
                    erreurs.append(f"{ou} : programme inconnu « {c} »")
                elif not cur["min"] <= v <= cur["max"]:
                    erreurs.append(f"{ou} : position de « {c} » hors bornes")
        for a in list(l.get("axes", {})) + [a for o in l.get("options", []) for a in o.get("axes", {})]:
            if a not in AXES:
                erreurs.append(f"{ou} : axe inconnu « {a} »")
    return erreurs


def donnees() -> dict:
    doc = lire_leviers()
    hyp_doc = yaml.safe_load(tr.HYPOTHESES.read_text(encoding="utf-8"))
    depart = tr.lire_depart()
    hypotheses, _ = tr.hypotheses_par_annee(hyp_doc, depart)
    reference = tr.projeter(depart, hypotheses)
    candidats = []
    for i, (_, p) in enumerate(lire_programmes()):
        a = agreger(p)
        ajust = {an: 100 * v / next(l["pib"] for l in reference if l["annee"] == an) for an, v in a["par_annee"]["central"].items()}
        dette = tr.projeter(depart, hypotheses, ajust)[-1]["dette"]
        choix = {}
        for l in doc["leviers"]:
            if l["type"] == "choix":
                o = next((o["id"] for o in l["options"] if p["id"] in o.get("candidats", [])), None)
                if o:
                    choix[l["id"]] = o
            elif p["id"] in l["curseur"].get("positions", {}):
                choix[l["id"]] = l["curseur"]["positions"][p["id"]]
        candidats.append({
            "id": p["id"], "nom": p["candidat"], "parti": p["parti"], "couleur": COULEURS[i % len(COULEURS)],
            "solde": a["croisiere"]["central"], "dette2032": dette, "choix": choix,
        })
    glossaire = yaml.safe_load(GLOSSAIRE.read_text(encoding="utf-8")) if GLOSSAIRE.exists() else []
    return {
        "genere": date.today().isoformat(),
        "axes": [{"id": k, "nom": n, "moins": m, "plus": p} for k, (n, m, p) in AXES.items()],
        "glossaire": glossaire,
        "annees": ANNEES,
        "montee": doc.get("montee_par_defaut") or {"2027": 0, "2028": 0.4, "2029": 0.7, "2030": 0.9, "2031": 1, "2032": 1},
        "leviers": doc["leviers"],
        "candidats": candidats,
        "depart": {"annee": depart.annee, "dette": depart.dette},
        "hypotheses": {str(a): h for a, h in hypotheses.items()},
        "reference": [{"annee": l["annee"], "dette": l["dette"], "pib": l["pib"]} for l in reference],
    }


COMMUN_CSS = r""".gl{border-bottom:1px dotted currentColor;cursor:help;position:relative}.gl:focus-visible{outline:2px solid var(--acc);outline-offset:2px}.gl sup{font-size:.6em;color:var(--acc);margin-left:1px}
.gl .def{display:none;position:absolute;left:50%;bottom:130%;transform:translateX(-50%);width:min(280px,80vw);background:var(--fg);color:var(--bg);
  font-size:.8rem;line-height:1.35;font-weight:400;text-align:left;padding:8px 10px;border-radius:8px;z-index:20;box-shadow:0 4px 14px #0004}
.gl:hover .def,.gl:focus .def{display:block}
.axes-l{margin:6px 0 4px}.axe-l{margin:10px 0}.axe-l .t{font-weight:600;font-size:.9rem}.axe-l .bornes{display:flex;justify-content:space-between;font-size:.72rem;color:var(--muted)}
.axe-l .rail{position:relative;height:22px;margin:2px 6px}.axe-l .rail:before{content:"";position:absolute;left:0;right:0;top:10px;height:2px;background:var(--line)}
.axe-l .rail .z{position:absolute;left:50%;top:5px;width:1px;height:12px;background:var(--muted)}
.axe-l .rail .p{position:absolute;top:6px;width:10px;height:10px;border-radius:50%;transform:translateX(-50%);opacity:.85}
.axe-l .rail .moi{position:absolute;top:2px;width:18px;height:18px;border-radius:50%;transform:translateX(-50%);background:var(--acc);border:3px solid var(--card);box-shadow:0 0 0 1px var(--acc)}
.legende{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:.75rem;margin:4px 0}.legende i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:3px}
"""

COMMUN_JS = r"""// --- Glossaire : première occurrence de chaque terme soulignée, définition au survol ou au toucher
const GL = (D.glossaire || []).flatMap(g => [g.terme, ...(g.variantes || [])].map(f => ({f, g})))
  .sort((a, b) => b.f.length - a.f.length);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));  // tout texte de données inséré en HTML passe par là
const echap = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
function annoter(texte) {
  const pris = [], morceaux = [];
  let s = esc(texte);
  for (const {f, g} of GL) {
    if (pris.includes(g.terme)) continue;
    const re = new RegExp(`(?<![\\p{L}\\d&])${echap(esc(f))}(?![\\p{L}\\d])`, /^[A-Z0-9]+$/.test(f) ? "u" : "iu");
    const m = s.match(re); if (!m) continue;
    pris.push(g.terme); morceaux.push(`<span class="gl" tabindex="0">${m[0]}<sup>?</sup><span class="def">${esc(g.definition)}</span></span>`);
    s = s.slice(0, m.index) + `\u0000${morceaux.length - 1}\u0000` + s.slice(m.index + m[0].length);
  }
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => morceaux[+i]);
}
// --- Axes thématiques : moyenne des scores (−2 à +2) des leviers de l'axe, droit en vigueur = 0
function scoresAxes(choix) {
  const r = {};
  for (const a of D.axes) {
    let s = 0, n = 0;
    for (const l of D.leviers) {
      if (l.type === "choix") {
        if (!l.options.some(o => o.axes && a.id in o.axes)) continue;
        const o = l.options.find(o => o.id === (choix[l.id] ?? defaut(l))); s += (o.axes || {})[a.id] || 0; n++;
      } else if (l.axes && a.id in l.axes) {
        const v = choix[l.id] ?? 0, borne = v >= 0 ? l.curseur.max : -l.curseur.min;
        s += l.axes[a.id] * 2 * (borne ? v / borne : 0); n++;
      }
    }
    if (n) r[a.id] = s / n;
  }
  return r;
}

function htmlAxes(choix) {
  const moi = scoresAxes(choix), cand = D.candidats.map(c => ({c, s: scoresAxes(c.choix)}));
  const x = v => 50 + 50 * v / 2;
  const lignes = D.axes.filter(a => a.id in moi).map(a => `<div class="axe-l"><div class="t">${esc(a.nom)}</div>
    <div class="rail"><span class="z"></span>${cand.map(({c, s}) => `<span class="p" title="${esc(c.nom)}" style="left:${x(s[a.id])}%;background:${esc(c.couleur)}"></span>`).join("")}
    <span class="moi" title="Vous" style="left:${x(moi[a.id])}%"></span></div>
    <div class="bornes"><span>← ${esc(a.moins)}</span><span>${esc(a.plus)} →</span></div></div>`).join("");
  return `<div class="legende"><span><i style="background:var(--acc)"></i><b>Vous</b></span>${D.candidats.map(c => `<span><i style="background:${esc(c.couleur)}"></i>${court(c)}</span>`).join("")}</div>
    <div class="axes-l">${lignes}</div><p class="petit">Chaque thème fait la moyenne de vos choix sur les décisions qui le concernent (droit actuel au centre). Les
    positions des candidats sont reconstituées à partir des mêmes décisions.</p>`;
}
"""


PAGE = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simulateur budgétaire 2027</title><style>
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#66645e;--line:#e2dfd7;--card:#fff;--neg:#b03a2e;--pos:#1e7a4a;--acc:#2451a6}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#161614;--fg:#ecebe6;--muted:#9a978f;--line:#34332f;--card:#1f1f1c;--neg:#e0796e;--pos:#6fcf97;--acc:#8fb0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
header{max-width:1200px;margin:0 auto;padding:24px 16px 8px}h1{font-size:1.6rem;margin:0 0 .3em}p.m{color:var(--muted);max-width:80ch;margin:.3em 0}
main{max-width:1200px;margin:0 auto;padding:8px 16px 64px;display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:24px;align-items:start}
@media (max-width:900px){main{grid-template-columns:1fr}aside{position:static!important}#mini{display:flex!important}body{padding-bottom:56px}}
#mini{display:none;position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:8px 16px;gap:16px;justify-content:space-between;align-items:center;font-variant-numeric:tabular-nums;z-index:5}
#mini b{font-size:1.1rem}#mini a{color:var(--acc)}
.barre{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 16px}button,select{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:6px 10px;cursor:pointer}
details.theme{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:0 0 10px}
details.theme>summary{padding:10px 14px;font-weight:650;cursor:pointer;display:flex;justify-content:space-between;gap:8px}
details.theme>summary .t{font-weight:400;color:var(--muted);font-variant-numeric:tabular-nums}
.levier{padding:10px 14px;border-top:1px solid var(--line)}.q{font-weight:600}.aide{color:var(--muted);font-size:.85rem;margin:.1em 0 .4em}
label.opt{display:grid;grid-template-columns:20px 1fr auto;gap:6px;align-items:start;padding:4px 6px;border-radius:6px;cursor:pointer}
label.opt:hover{background:color-mix(in srgb,var(--acc) 7%,transparent)}label.opt input{margin-top:4px}
.eff{font-variant-numeric:tabular-nums;white-space:nowrap;font-size:.9rem}.neg{color:var(--neg)}.pos{color:var(--pos)}
.tags{grid-column:2/4;display:flex;gap:4px;flex-wrap:wrap}.tag{font-size:.72rem;border-radius:10px;padding:0 7px;color:#fff}
.curseur{display:flex;align-items:center;gap:10px}.curseur input{flex:1}.pos-c{position:relative;height:14px;margin:0 0 2px}
.pos-c span{position:absolute;top:0;width:8px;height:8px;border-radius:50%;transform:translateX(-50%)}
aside{position:sticky;top:12px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.gros{font-size:2rem;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}.petit{color:var(--muted);font-size:.8rem}
.kpis{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}h3{font-size:.95rem;margin:14px 0 4px}
svg{width:100%;height:auto;display:block}.grille{stroke:var(--line)}.axe{fill:var(--muted);font-size:10px}
ol.proches{margin:4px 0;padding-left:18px}ol.proches li{margin:3px 0}ol.proches .ligne{display:flex;align-items:center;gap:6px;flex-wrap:wrap}.barre-acc{height:6px;border-radius:3px;background:var(--acc);display:inline-block;vertical-align:middle;margin-left:6px}
__COMMUN_CSS__
footer{max-width:1200px;margin:0 auto;padding:0 16px 40px;color:var(--muted);font-size:.8rem}
</style></head><body>
<header><h1>Et vous, quel budget ?</h1>
<p class="m">Prenez les décisions que les candidats à la présidentielle 2027 mettent en débat. Chaque option est chiffrée avec
la même méthode que le chiffrage des programmes : effet sur le solde public en 2032, par rapport au droit en vigueur, sans effet
de second tour. Votre dette 2032 et les candidats dont vous êtes le plus proche se mettent à jour à chaque choix.</p>
<div class="barre"><button id="raz">Tout remettre au droit actuel</button>
<select id="depart" aria-label="Partir du programme d'un candidat"><option value="">Partir du programme de…</option></select>
<button id="partager">Copier le lien de mon budget</button></div></header>
<main><div id="leviers"></div>
<aside id="resultats"><div class="kpis"><div><div class="petit">Solde en 2032, par an</div><div class="gros" id="solde" aria-live="polite">0</div><div class="petit" id="fourchette"></div></div>
<div><div class="petit">Dette publique en 2032</div><div class="gros" id="dette" aria-live="polite"></div><div class="petit" id="dette-ref"></div></div></div>
<svg id="courbe" viewBox="0 0 380 170" role="img" aria-label="Trajectoire de la dette publique jusqu'en 2032 : votre budget, le droit actuel et les candidats"></svg>
<h3>Où vous situez-vous ?</h3><svg id="carte" viewBox="0 0 380 300" role="img" aria-label="Carte des dépenses et des impôts : vous et les candidats"></svg>
<div class="petit">Axe horizontal : dépenses publiques en plus ou en moins ; axe vertical : impôts et cotisations en plus ou en
moins, en Md€ par an en 2032, d'après les leviers de cette page.</div>
<h3>Vos positions par thème</h3><div id="axes"></div>
<h3>Candidats les plus proches de vos choix</h3><ol class="proches" id="proches"></ol>
<div class="petit">Part des leviers où votre choix est celui du candidat, sur les seuls leviers où son programme prend position.</div></aside></main>
<div id="mini"><span>Solde 2032 <b id="mini-solde"></b></span><span>Dette <b id="mini-dette"></b></span><a href="#resultats">Résultats ↓</a></div>
<footer>Données du __GENERE__. Montée en charge des mesures : convention commune ; trajectoire : hypothèses du FMI, solde
primaire de référence gelé. Méthode, sources et chiffrage détaillé des programmes : rapport de chiffrage du même dépôt.</footer>
<script>
const D = __DONNEES__;
const fmt = (x, s = true) => (s && x > 0 ? "+" : "") + x.toFixed(1).replace(".", ",").replace("-", "−");
const etat = {};
const parTheme = {}, themes = [];
D.leviers.forEach(l => (parTheme[l.theme] ??= []).push(l));
Object.keys(parTheme).forEach(t => themes.push(t));
const defaut = l => l.type === "choix" ? l.options.find(o => o.defaut).id : 0;
__COMMUN_JS__
const candidat = id => D.candidats.find(c => c.id === id);
const court = c => esc(c.nom.split(" ").slice(1).join(" "));  // déjà échappé : uniquement pour du HTML
function placer(occupees, x, y) {  // décale verticalement une étiquette qui en chevauche une autre
  let yy = y;
  while (occupees.some(o => Math.abs(o.x - x) < 70 && Math.abs(o.y - yy) < 11)) yy += 11;
  occupees.push({x, y: yy}); return yy;
}

function effet(l, v) {
  if (l.type === "choix") { const o = l.options.find(o => o.id === v); return {...o.effet, montee: o.montee}; }
  const k = (l.curseur.md_par_unite ?? 1) * v * (l.axe === "depenses" ? -1 : 1);
  return {central: k, bas: k, haut: k};
}
function mouvements(choix) {
  let dep = 0, prel = 0;
  for (const l of D.leviers) {
    const e = effet(l, choix[l.id] ?? defaut(l)).central;
    if (l.axe === "depenses") dep -= e; else prel += e;
  }
  return {dep, prel};
}
function projeter(par_annee) {
  let dette = D.depart.dette; const serie = [{annee: D.depart.annee, dette}];
  for (const [a, h] of Object.entries(D.hypotheses)) {
    const g = (1 + h.croissance / 100) * (1 + h.inflation / 100) - 1, t = h.taux / 100;
    const pib = D.reference.find(r => r.annee == a).pib;
    const sp = h.solde_primaire + 100 * (par_annee[a] || 0) / pib;
    dette = dette * (1 + t) / (1 + g) - sp; serie.push({annee: +a, dette});
  }
  return serie;
}
function calculer() {
  const tot = {central: 0, bas: 0, haut: 0}, par_annee = {};
  for (const l of D.leviers) {
    const e = effet(l, etat[l.id]); const m = e.montee || D.montee;
    for (const k of ["central", "bas", "haut"]) tot[k] += e[k];
    for (const a of D.annees) par_annee[a] = (par_annee[a] || 0) + e.central * (m[a] ?? 1);
  }
  return {tot, serie: projeter(par_annee)};
}
function accord(c) {
  let s = 0, n = 0;
  for (const l of D.leviers) {
    if (!(l.id in c.choix)) continue;
    n++;
    if (l.type === "choix") s += c.choix[l.id] === etat[l.id] ? 1 : 0;
    else s += 1 - Math.abs(c.choix[l.id] - etat[l.id]) / (l.curseur.max - l.curseur.min);
  }
  return n ? {pct: 100 * s / n, n} : {pct: 0, n: 0};
}
function tags(o) {
  return (o.candidats || []).map(id => { const c = candidat(id); return c ? `<span class="tag" style="background:${esc(c.couleur)}">${court(c)}</span>` : ""; }).join("");
}
function rendreLeviers() {
  const racine = document.getElementById("leviers"); racine.innerHTML = "";
  for (const [theme, ls] of Object.entries(parTheme)) {
    const d = document.createElement("details"); d.className = "theme"; d.open = true;
    d.innerHTML = `<summary>${esc(theme)}<span class="t" data-i="${themes.indexOf(theme)}"></span></summary>`;
    for (const l of ls) {
      const div = document.createElement("div"); div.className = "levier";
      let h = `<div class="q">${annoter(l.question)}</div>${l.aide ? `<div class="aide">${annoter(l.aide)}</div>` : ""}`;
      if (l.type === "choix") {
        for (const o of l.options) {
          const e = o.effet.central;
          h += `<label class="opt"><input type="radio" name="${esc(l.id)}" value="${esc(o.id)}" ${etat[l.id] === o.id ? "checked" : ""}>
            <span>${esc(o.libelle)}</span><span class="eff ${e < 0 ? "neg" : e > 0 ? "pos" : ""}">${e ? fmt(e) + " Md€" : "—"}</span>
            <span class="tags">${tags(o)}</span></label>`;
        }
      } else {
        const c = l.curseur, pos = Object.entries(c.positions || {}).map(([id, v]) => {
          const k = candidat(id); return k ? `<span title="${esc(k.nom)} : ${esc(v)}" style="left:${100 * (v - c.min) / (c.max - c.min)}%;background:${esc(k.couleur)}"></span>` : ""; }).join("");
        h += `<div class="pos-c">${pos}</div><div class="curseur"><input type="range" name="${esc(l.id)}" aria-label="${esc(l.question)}" min="${c.min}" max="${c.max}" step="${c.pas}" value="${etat[l.id]}">
          <span class="eff" id="v-${esc(l.id)}"></span></div>`;
      }
      div.innerHTML = h; d.appendChild(div);
    }
    racine.appendChild(d);
  }
  racine.addEventListener("input", ev => {
    const l = D.leviers.find(l => l.id === ev.target.name); if (!l) return;
    etat[l.id] = l.type === "choix" ? ev.target.value : +ev.target.value; majResultats();
  });
}
function svgCourbe(serie) {
  const W = 380, H = 170, g = 30, dr = 18, hh = 10, b = 20;
  const toutes = [...serie, ...D.reference, ...D.candidats.map(c => ({dette: c.dette2032}))].map(p => p.dette);
  const lo = Math.floor(Math.min(...toutes) / 10) * 10, hi = Math.ceil(Math.max(...toutes) / 10) * 10;
  const x = a => g + (a - D.depart.annee) / (2032 - D.depart.annee) * (W - g - dr), y = v => hh + (hi - v) / (hi - lo) * (H - hh - b);
  let s = "";
  for (let v = lo; v <= hi; v += 10) s += `<line x1="${g}" x2="${W - dr}" y1="${y(v)}" y2="${y(v)}" class="grille"/><text x="${g - 4}" y="${y(v) + 3}" text-anchor="end" class="axe">${v}</text>`;
  for (const a of [D.depart.annee, 2028, 2030, 2032]) s += `<text x="${x(a)}" y="${H - 5}" text-anchor="middle" class="axe">${a}</text>`;
  for (const c of D.candidats) s += `<circle cx="${x(2032)}" cy="${y(c.dette2032)}" r="3" fill="${esc(c.couleur)}" opacity=".7"><title>${esc(c.nom)} : ${fmt(c.dette2032, false)} %</title></circle>`;
  s += `<polyline fill="none" stroke="var(--muted)" stroke-dasharray="4 3" stroke-width="1.5" points="${D.reference.map(p => `${x(p.annee)},${y(p.dette)}`).join(" ")}"/>`;
  s += `<polyline fill="none" stroke="var(--acc)" stroke-width="2.5" points="${serie.map(p => `${x(p.annee)},${y(p.dette)}`).join(" ")}"/>`;
  return s;
}
function svgCarte(moi) {
  const W = 380, H = 300, m = 30;
  const pts = D.candidats.map(c => ({...mouvements(c.choix), c})); pts.push({...moi, moi: true});
  const lim = Math.max(20, ...pts.flatMap(p => [Math.abs(p.dep), Math.abs(p.prel)])) * 1.1;
  const x = v => W / 2 + v / lim * (W / 2 - m), y = v => H / 2 - v / lim * (H / 2 - m);
  let s = `<line x1="${m}" x2="${W - m}" y1="${H / 2}" y2="${H / 2}" class="grille"/><line y1="${m / 2}" y2="${H - m / 2}" x1="${W / 2}" x2="${W / 2}" class="grille"/>
    <text x="${W - m}" y="${H / 2 - 5}" text-anchor="end" class="axe">plus de dépenses →</text><text x="${m}" y="${H / 2 - 5}" class="axe">← moins de dépenses</text>
    <text x="${W / 2 + 5}" y="${m / 2 + 8}" class="axe">↑ plus d'impôts</text><text x="${W / 2 + 5}" y="${H - m / 2}" class="axe">↓ moins d'impôts</text>`;
  const occ = [];
  for (const p of [...pts].sort((a, b) => (b.moi ? 1 : 0) - (a.moi ? 1 : 0))) {
    const ly = placer(occ, x(p.dep), y(p.prel));
    if (p.moi) s += `<circle cx="${x(p.dep)}" cy="${y(p.prel)}" r="8" fill="var(--acc)" stroke="var(--card)" stroke-width="2"><title>Vous</title></circle><text x="${x(p.dep) + 10}" y="${ly + 4}" font-size="11" font-weight="700" fill="var(--acc)">Vous</text>`;
    else s += `<circle cx="${x(p.dep)}" cy="${y(p.prel)}" r="5" fill="${esc(p.c.couleur)}"><title>${esc(p.c.nom)} : dépenses ${fmt(p.dep)}, prélèvements ${fmt(p.prel)} Md€</title></circle><text x="${x(p.dep) + (x(p.dep) > W - 90 ? -7 : 7)}" y="${ly + 3}" text-anchor="${x(p.dep) > W - 90 ? "end" : "start"}" font-size="10" fill="${esc(p.c.couleur)}">${court(p.c)}</text>`;
  }
  return s;
}
function majResultats() {
  const {tot, serie} = calculer();
  const el = document.getElementById("solde"); el.textContent = fmt(tot.central) + " Md€"; el.className = "gros " + (tot.central < 0 ? "neg" : tot.central > 0 ? "pos" : "");
  document.getElementById("fourchette").textContent = `fourchette ${fmt(tot.bas)} à ${fmt(tot.haut)} Md€`;
  const d = serie.at(-1).dette, ref = D.reference.at(-1).dette;
  document.getElementById("dette").textContent = fmt(d, false) + " %";
  document.getElementById("mini-solde").textContent = fmt(tot.central) + " Md€"; document.getElementById("mini-solde").className = tot.central < 0 ? "neg" : tot.central > 0 ? "pos" : "";
  document.getElementById("mini-dette").textContent = fmt(d, false) + " %";
  document.getElementById("dette-ref").textContent = `droit actuel : ${fmt(ref, false)} % du PIB`;
  document.getElementById("courbe").innerHTML = svgCourbe(serie);
  document.getElementById("carte").innerHTML = svgCarte(mouvements(etat));
  document.getElementById("axes").innerHTML = htmlAxes(etat);
  const cl = D.candidats.map(c => ({c, ...accord(c)})).filter(r => r.n).sort((a, b) => b.pct - a.pct);
  document.getElementById("proches").innerHTML = cl.map(r => `<li><div class="ligne"><span style="color:${esc(r.c.couleur)};font-weight:600">${esc(r.c.nom)}</span><span class="barre-acc" style="width:${r.pct * 0.6}px"></span>
    <span class="petit">${Math.round(r.pct)} % d'accord sur ${r.n} levier${r.n > 1 ? "s" : ""}</span></div></li>`).join("");
  for (const [theme, ls] of Object.entries(parTheme)) {
    const t = ls.reduce((s, l) => s + effet(l, etat[l.id]).central, 0);
    const span = document.querySelector(`[data-i="${themes.indexOf(theme)}"]`); if (span) { span.textContent = t ? fmt(t) + " Md€" : ""; span.className = "t " + (t < 0 ? "neg" : t > 0 ? "pos" : ""); }
  }
  for (const l of D.leviers) if (l.type === "curseur") {
    const v = etat[l.id], e = effet(l, v).central; const s = document.getElementById("v-" + l.id);
    if (s) { s.textContent = `${v > 0 ? "+" : ""}${v} ${l.curseur.unite}`; s.className = "eff " + (e < 0 ? "neg" : e > 0 ? "pos" : ""); }
  }
  try { history.replaceState(null, "", "#b=" + encodeURIComponent(JSON.stringify(etat))); } catch (e) {}
}
function charger(choix) {
  for (const l of D.leviers) etat[l.id] = choix && l.id in choix ? choix[l.id] : defaut(l);
  rendreLeviers(); majResultats();
}
const sel = document.getElementById("depart");
for (const c of D.candidats) sel.insertAdjacentHTML("beforeend", `<option value="${esc(c.id)}">${esc(c.nom)}</option>`);
sel.onchange = () => { if (sel.value) charger(candidat(sel.value).choix); sel.value = ""; };
document.getElementById("raz").onclick = () => charger(null);
document.getElementById("partager").onclick = () => { navigator.clipboard?.writeText(location.href); };
let initial = null; try { if (location.hash.startsWith("#b=")) initial = JSON.parse(decodeURIComponent(location.hash.slice(3))); } catch (e) {}
charger(initial);
</script></body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--valider", action="store_true")
    args = parser.parse_args(argv)
    if not LEVIERS.exists():
        print("chiffrage/simulateur.yaml absent : simulateur non généré")
        return 0
    erreurs = valider()
    for e in erreurs:
        print(f"ÉCHEC {e}", file=sys.stderr)
    if erreurs or args.valider:
        print(f"{len(erreurs)} erreur(s).")
        return 1 if erreurs else 0
    d = donnees()
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(remplir(PAGE, COMMUN_JS=COMMUN_JS, COMMUN_CSS=COMMUN_CSS, DONNEES=json_pour_script(d), GENERE=d["genere"]), encoding="utf-8")
    print(f"-> {SORTIE.relative_to(RACINE)} ({len(d['leviers'])} leviers, {len(d['candidats'])} candidats)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
