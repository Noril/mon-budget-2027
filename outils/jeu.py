"""Jeu de cartes façon « Reigns » : un dilemme par carte, glisser à gauche ou à droite, un programme se forme.

    uv run python -m outils.jeu              # valide chiffrage/cartes.yaml, écrit build/jeu.html
    uv run python -m outils.jeu --valider

Les cartes (chiffrage/cartes.yaml) fixent les leviers du simulateur (chiffrage/simulateur.yaml) ; les montants, la
trajectoire de dette et la proximité avec les candidats sont ceux du simulateur (outils/simulateur.py).
"""

from __future__ import annotations

import argparse
import json
import sys

import yaml

from pipelines.commun import RACINE

from .simulateur import COMMUN_CSS, COMMUN_JS, donnees, lire_leviers

CARTES = RACINE / "chiffrage" / "cartes.yaml"
SORTIE = RACINE / "build" / "jeu.html"


def lire_cartes() -> dict:
    return yaml.safe_load(CARTES.read_text(encoding="utf-8"))


def valider(doc: dict | None = None) -> list[str]:
    if not CARTES.exists():
        return []
    doc = doc or lire_cartes()
    leviers = {l["id"]: l for l in lire_leviers()["leviers"]}
    persos = {p["id"] for p in doc.get("personnages", [])}
    cartes = doc.get("cartes", [])
    ids = [c.get("id") for c in cartes]
    erreurs = [f"cartes.yaml : carte « {i} » en double" for i in sorted({i for i in ids if ids.count(i) > 1})]
    if cartes and cartes[0].get("suite_seulement"):
        erreurs.append("cartes.yaml : la première carte ne peut pas être une suite")
    for c in cartes:
        ou = f"cartes.yaml:{c.get('id')}"
        for champ in ("id", "personnage", "levier", "texte", "gauche", "droite"):
            if champ not in c:
                erreurs.append(f"{ou} : champ « {champ} » manquant")
        if c.get("personnage") not in persos:
            erreurs.append(f"{ou} : personnage inconnu « {c.get('personnage')} »")
        l = leviers.get(c.get("levier"))
        if l is None:
            erreurs.append(f"{ou} : levier inconnu « {c.get('levier')} »")
            continue
        for cote in ("gauche", "droite"):
            choix = c.get(cote) or {}
            if not choix.get("libelle"):
                erreurs.append(f"{ou} : {cote} sans libellé")
            if l["type"] == "choix":
                if choix.get("option") not in {o["id"] for o in l["options"]}:
                    erreurs.append(f"{ou} : {cote} renvoie à une option inconnue « {choix.get('option')} »")
            elif not isinstance(choix.get("valeur"), (int, float)) or not l["curseur"]["min"] <= choix["valeur"] <= l["curseur"]["max"]:
                erreurs.append(f"{ou} : {cote} demande une valeur dans les bornes du curseur")
            if (s := choix.get("suite")) and s not in ids:
                erreurs.append(f"{ou} : suite inconnue « {s} »")
    return erreurs


PAGE = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Élysée 2027 : le jeu du budget</title><style>
:root{--bg:#f4f1ea;--fg:#1d1d1b;--muted:#77756f;--line:#dcd8cd;--card:#fffdf8;--neg:#b03a2e;--pos:#1e7a4a;--acc:#2451a6}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141412;--fg:#ecebe6;--muted:#9a978f;--line:#34332f;--card:#1f1f1c;--neg:#e0796e;--pos:#6fcf97;--acc:#8fb0ff}}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;overscroll-behavior:none}
#app{max-width:440px;margin:0 auto;min-height:100%;display:flex;flex-direction:column;padding:14px 16px 20px}
.jauges{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.jauge{text-align:center;font-size:.75rem;color:var(--muted)}.jauge .ic{font-size:1.4rem;display:block}
.jauge .val{font-weight:700;color:var(--fg);font-variant-numeric:tabular-nums;font-size:.95rem}
.piste{position:relative;height:10px;border-radius:4px;background:var(--line);margin:4px 0;overflow:hidden}
.piste i{position:absolute;top:0;bottom:0;border-radius:4px;transition:all .35s}
.piste b{position:absolute;top:-2px;bottom:-2px;width:2px;background:var(--muted)}
.apercu{height:14px;font-size:.72rem;font-weight:700}
#table{flex:1;display:flex;align-items:center;justify-content:center;position:relative;min-height:400px;margin-top:10px;touch-action:none}
.carte{position:absolute;width:100%;max-width:380px;background:var(--card);border:1px solid var(--line);border-radius:18px;
  box-shadow:0 8px 30px #0002;padding:18px 18px 22px;user-select:none;cursor:grab;will-change:transform}
.carte.anim{transition:transform .3s ease,opacity .3s}
.choix-haut{display:flex;justify-content:space-between;gap:8px;min-height:44px;font-weight:700;font-size:.95rem}
.choix-haut span{opacity:0;transition:opacity .1s;max-width:48%}.choix-haut .d{text-align:right}
.perso{font-size:4.2rem;text-align:center;line-height:1;margin:6px 0}
.nom{text-align:center;font-weight:700;margin-bottom:10px}
.texte{font-size:1.1rem;text-align:center;min-height:5.5em}
.boutons,.impacts{display:grid;grid-template-columns:1fr 1fr;gap:10px}.boutons{margin-top:14px}
.impacts{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line);text-align:center}
.boutons button{font:inherit;font-size:.85rem;padding:10px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
__COMMUN_CSS__
.impact{display:block;font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}
.bas{display:flex;justify-content:space-between;color:var(--muted);font-size:.8rem;margin-top:10px}
.bas a{color:var(--acc)}
.fin h1{font-size:1.5rem;margin:.4em 0 .2em}.fin .kpi{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.fin .gros{font-size:1.8rem;font-weight:800;font-variant-numeric:tabular-nums}.petit{color:var(--muted);font-size:.8rem}
.fin ul{padding-left:18px;margin:.3em 0}.fin li{margin:3px 0}.neg{color:var(--neg)}.pos{color:var(--pos)}
.fin button,.fin a.bt{display:inline-block;font:inherit;padding:10px 14px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);text-decoration:none;cursor:pointer;margin:4px 6px 4px 0}
.accueil{text-align:center}.accueil h1{font-size:1.7rem;margin:.6em 0 .2em}.accueil p{color:var(--muted)}
.accueil button{font:inherit;font-size:1.05rem;padding:12px 22px;border-radius:12px;border:0;background:var(--acc);color:#fff;cursor:pointer;margin-top:10px}
svg{width:100%;height:auto;display:block}.grille{stroke:var(--line)}.axe{fill:var(--muted);font-size:10px}
.barre-acc{height:6px;border-radius:3px;background:var(--acc);display:inline-block;vertical-align:middle;margin:0 6px}
</style></head><body><div id="app"></div>
<script>
const D = __DONNEES__;
const C = __CARTES__;
const fmt = (x, s = true) => (s && x > 0 ? "+" : "") + x.toFixed(1).replace(".", ",").replace("-", "−");
const levier = id => D.leviers.find(l => l.id === id);
const perso = id => C.personnages.find(p => p.id === id);
const defaut = l => l.type === "choix" ? l.options.find(o => o.defaut).id : 0;
const court = c => c.nom.split(" ").slice(1).join(" ");
function placer(occupees, x, y) {  // décale verticalement une étiquette qui en chevauche une autre
  let yy = y;
  while (occupees.some(o => Math.abs(o.x - x) < 70 && Math.abs(o.y - yy) < 11)) yy += 11;
  occupees.push({x, y: yy}); return yy;
}
function effet(l, v) {
  if (l.type === "choix") { const o = l.options.find(o => o.id === v); return {...o.effet, montee: o.montee}; }
  const k = (l.curseur.md_par_unite ?? 1) * v * (l.axe === "depenses" ? -1 : 1); return {central: k, bas: k, haut: k};
}
function bilan(choix) {
  let dep = 0, prel = 0, solde = 0, bas = 0, haut = 0; const par_annee = {};
  for (const l of D.leviers) {
    const e = effet(l, choix[l.id] ?? defaut(l)), m = e.montee || D.montee;
    solde += e.central; bas += e.bas; haut += e.haut;
    if (l.axe === "depenses") dep -= e.central; else prel += e.central;
    for (const a of D.annees) par_annee[a] = (par_annee[a] || 0) + e.central * (m[a] ?? 1);
  }
  let dette = D.depart.dette;
  for (const [a, h] of Object.entries(D.hypotheses)) {
    const g = (1 + h.croissance / 100) * (1 + h.inflation / 100) - 1, t = h.taux / 100, pib = D.reference.find(r => r.annee == a).pib;
    dette = dette * (1 + t) / (1 + g) - (h.solde_primaire + 100 * (par_annee[a] || 0) / pib);
  }
  return {dep, prel, solde, bas, haut, dette};
}
function accord(c, choix) {
  let s = 0, n = 0;
  for (const l of D.leviers) {
    if (!(l.id in c.choix)) continue; n++;
    const v = choix[l.id] ?? defaut(l);
    s += l.type === "choix" ? (c.choix[l.id] === v ? 1 : 0) : 1 - Math.abs(c.choix[l.id] - v) / (l.curseur.max - l.curseur.min);
  }
  return {pct: n ? 100 * s / n : 0, n};
}

__COMMUN_JS__
const JAUGES = [
  {id: "dette", ic: "📈", nom: "Dette 2032", min: 115, max: 175, ref: D.reference.at(-1).dette, f: b => b.dette, u: " %", mauvais: +1},
  {id: "dep", ic: "🏛️", nom: "Dépenses", min: -120, max: 120, ref: 0, f: b => b.dep, u: " Md€"},
  {id: "prel", ic: "🧾", nom: "Impôts", min: -120, max: 120, ref: 0, f: b => b.prel, u: " Md€"},
];
let choix = {}, file = [], vues = 0, total = 0, historique = [];
const app = document.getElementById("app");

function htmlJauges() {
  return `<div class="jauges">${JAUGES.map(j => `<div class="jauge"><span class="ic">${j.ic}</span>${j.nom}
    <div class="piste"><b style="left:${pos(j, j.ref)}%"></b><i id="bar-${j.id}"></i></div>
    <div class="val" id="val-${j.id}"></div><div class="apercu" id="ap-${j.id}"></div></div>`).join("")}</div>`;
}
const pos = (j, v) => Math.max(0, Math.min(100, 100 * (v - j.min) / (j.max - j.min)));
function majJauges(apres) {
  const b = bilan(choix);
  for (const j of JAUGES) {
    const v = j.f(b), bar = document.getElementById("bar-" + j.id), x0 = pos(j, j.ref), x1 = pos(j, v);
    bar.style.left = Math.min(x0, x1) + "%"; bar.style.width = (Math.abs(v - j.ref) < 0.05 ? 0 : Math.max(3, Math.abs(x1 - x0))) + "%";
    bar.style.background = j.id === "dette" ? (v > j.ref + 0.05 ? "var(--neg)" : "var(--pos)") : "var(--acc)";
    document.getElementById("val-" + j.id).textContent = j.id === "dette" ? fmt(v, false) + j.u : fmt(v) + j.u;
    const ap = document.getElementById("ap-" + j.id);
    if (apres) {
      const d = j.f(bilan(apres)) - v;
      ap.textContent = Math.abs(d) < 0.05 ? "" : (d > 0 ? "▲ " : "▼ ") + fmt(Math.abs(d), false);
      ap.style.color = j.id === "dette" ? (d > 0 ? "var(--neg)" : "var(--pos)") : "var(--muted)";
    } else ap.textContent = "";
  }
}
function impact(carte, cote) {
  // effet du choix par rapport à la situation actuelle : solde 2032 et dette 2032
  const avant = bilan(choix), apres = bilan(avec(carte, cote)), ds = apres.solde - avant.solde, dd = apres.dette - avant.dette;
  const cls = x => x < -0.05 ? "neg" : x > 0.05 ? "pos" : "";
  const solde = Math.abs(ds) < 0.05 ? "sans effet" : `${fmt(ds)} Md€/an`;
  return `<span class="impact"><b class="${cls(ds)}">${solde}</b><br>${Math.abs(dd) < 0.05 ? "&nbsp;" : `dette <b class="${cls(-dd)}">${dd > 0 ? "+" : "−"}${fmt(Math.abs(dd), false)} pt</b>`}</span>`;
}
function valeur(carte, cote) { const c = carte[cote]; return "option" in c ? c.option : c.valeur; }
function avec(carte, cote) { return {...choix, [carte.levier]: valeur(carte, cote)}; }

function accueil() {
  app.innerHTML = `<div class="accueil"><div style="font-size:4rem;margin-top:12vh">🏛️</div><h1>Élysée 2027 : le jeu du budget</h1>
    <p>Vous venez d'être élu·e. Chaque carte est une décision que les candidats mettent en débat. Glissez à gauche ou à droite :
    votre programme se construit, et sa facture aussi.</p>
    <p class="petit">Montants chiffrés avec la même méthode que les programmes des candidats (effet sur le solde public en 2032, sans
    effet de second tour). Personnages fictifs.</p><button id="go">Commencer</button></div>`;
  document.getElementById("go").onclick = demarrer;
}
function demarrer() {
  choix = {}; historique = []; vues = 0;
  file = C.cartes.filter(c => !c.suite_seulement).map(c => c.id);
  total = file.length;
  app.innerHTML = htmlJauges() + `<div id="table"></div><div class="bas"><span id="compteur"></span><a href="#" id="annuler">↶ Carte précédente</a></div>`;
  document.getElementById("annuler").onclick = e => { e.preventDefault(); annuler(); };
  suivante();
}
function annuler() {
  const h = historique.pop(); if (!h) return;
  if (!document.getElementById("table")) {  // depuis l'écran final : on retrouve la table de jeu
    app.innerHTML = htmlJauges() + `<div id="table"></div><div class="bas"><span id="compteur"></span><a href="#" id="annuler">↶ Carte précédente</a></div>`;
    document.getElementById("annuler").onclick = e => { e.preventDefault(); annuler(); };
  }
  choix = h.choix; file = h.file; vues = h.vues; total = h.total; suivante();
}
function suivante() {
  majJauges();
  if (!file.length) return fin();
  const carte = C.cartes.find(c => c.id === file[0]), p = perso(carte.personnage);
  document.getElementById("compteur").textContent = `Décision ${vues + 1} / ${total}`;
  const t = document.getElementById("table");
  t.innerHTML = `<div class="carte" id="carte" style="border-top:6px solid ${p.couleur}">
    <div class="choix-haut"><span class="g">← ${carte.gauche.libelle}</span><span class="d">${carte.droite.libelle} →</span></div>
    <div class="perso">${p.emoji}</div><div class="nom" style="color:${p.couleur}">${p.nom}</div>
    <div class="texte">${annoter(carte.texte)}</div>
    <div class="boutons"><button id="bg">← ${carte.gauche.libelle}</button><button id="bd">${carte.droite.libelle} →</button></div>
    <div class="impacts"><div>${impact(carte, "gauche")}</div><div>${impact(carte, "droite")}</div></div></div>`;
  const el = document.getElementById("carte"), g = el.querySelector(".g"), d = el.querySelector(".d");
  let x0 = null, dx = 0;
  const montrer = () => {
    g.style.opacity = dx < -20 ? Math.min(1, -dx / 90) : 0; d.style.opacity = dx > 20 ? Math.min(1, dx / 90) : 0;
    majJauges(dx < -20 ? avec(carte, "gauche") : dx > 20 ? avec(carte, "droite") : null);
  };
  el.addEventListener("pointerdown", e => { if (e.target.tagName === "BUTTON" || e.target.closest(".gl")) return; x0 = e.clientX; el.setPointerCapture(e.pointerId); el.classList.remove("anim"); });
  el.addEventListener("pointermove", e => { if (x0 === null) return; dx = e.clientX - x0; el.style.transform = `translateX(${dx}px) rotate(${dx / 18}deg)`; montrer(); });
  const lacher = () => { if (x0 === null) return; x0 = null;
    if (Math.abs(dx) > 90) decider(carte, dx < 0 ? "gauche" : "droite");
    else { el.classList.add("anim"); el.style.transform = ""; dx = 0; montrer(); } };
  el.addEventListener("pointerup", lacher); el.addEventListener("pointercancel", lacher);
  document.getElementById("bg").onclick = () => decider(carte, "gauche");
  document.getElementById("bd").onclick = () => decider(carte, "droite");
  const bg = document.getElementById("bg"), bd = document.getElementById("bd");
  for (const [b, c] of [[bg, "gauche"], [bd, "droite"]]) { b.onmouseenter = () => majJauges(avec(carte, c)); b.onmouseleave = () => majJauges(); }
}
function decider(carte, cote) {
  historique.push({choix: {...choix}, file: [...file], vues, total});
  const el = document.getElementById("carte");
  el.classList.add("anim"); el.style.transform = `translateX(${cote === "gauche" ? -600 : 600}px) rotate(${cote === "gauche" ? -30 : 30}deg)`; el.style.opacity = 0;
  choix[carte.levier] = valeur(carte, cote);
  file.shift(); vues++;
  const s = carte[cote].suite; if (s) { file.unshift(s); total++; }
  setTimeout(suivante, 260);
}
document.addEventListener("keydown", e => {
  const el = document.getElementById("carte"); if (!el) return;
  if (e.key === "Backspace") { e.preventDefault(); annuler(); return; }
  if (e.key === "ArrowLeft") document.getElementById("bg").click(); if (e.key === "ArrowRight") document.getElementById("bd").click();
});

function carte(b) {
  const W = 380, H = 260, m = 26, pts = D.candidats.map(c => ({...bilan(c.choix), c})); pts.push({...b, moi: true});
  const lim = Math.max(20, ...pts.flatMap(p => [Math.abs(p.dep), Math.abs(p.prel)])) * 1.1;
  const x = v => W / 2 + v / lim * (W / 2 - m), y = v => H / 2 - v / lim * (H / 2 - m);
  let s = `<line x1="${m}" x2="${W - m}" y1="${H / 2}" y2="${H / 2}" class="grille"/><line y1="8" y2="${H - 8}" x1="${W / 2}" x2="${W / 2}" class="grille"/>
    <text x="${W - m}" y="${H / 2 - 5}" text-anchor="end" class="axe">plus de dépenses →</text><text x="${m}" y="${H / 2 - 5}" class="axe">← moins</text>
    <text x="${W / 2 + 5}" y="16" class="axe">↑ plus d'impôts</text><text x="${W / 2 + 5}" y="${H - 8}" class="axe">↓ moins d'impôts</text>`;
  const occ = [];
  for (const p of [...pts].sort((a, b) => (b.moi ? 1 : 0) - (a.moi ? 1 : 0))) {
    const X = x(p.dep), Y = y(p.prel), fin = X > W - 90, ly = placer(occ, X, Y);
    s += p.moi ? `<circle cx="${X}" cy="${Y}" r="8" fill="var(--acc)" stroke="var(--card)" stroke-width="2"/><text x="${X + 11}" y="${ly + 4}" font-size="11" font-weight="700" fill="var(--acc)">Vous</text>`
      : `<circle cx="${X}" cy="${Y}" r="5" fill="${p.c.couleur}"/><text x="${X + (fin ? -7 : 7)}" y="${ly + 3}" text-anchor="${fin ? "end" : "start"}" font-size="10" fill="${p.c.couleur}">${court(p.c)}</text>`;
  }
  return `<svg viewBox="0 0 ${W} ${H}">${s}</svg>`;
}
function fin() {
  const b = bilan(choix), ref = D.reference.at(-1).dette;
  const faits = D.leviers.filter(l => (choix[l.id] ?? defaut(l)) !== defaut(l)).map(l => {
    const v = choix[l.id], e = effet(l, v).central;
    const lib = l.type === "choix" ? l.options.find(o => o.id === v).libelle : `${l.question.replace(/ \?$/, "")} : ${v > 0 ? "+" : ""}${v} ${l.curseur.unite}`;
    return {lib, e};
  }).sort((a, b) => a.e - b.e);
  const proches = D.candidats.map(c => ({c, ...accord(c, choix)})).filter(r => r.n).sort((a, b) => b.pct - a.pct);
  const lien = "simulateur.html#b=" + encodeURIComponent(JSON.stringify(choix));
  app.innerHTML = `<div class="fin"><h1>Votre programme</h1>
    <div class="kpi"><div><div class="petit">Solde en 2032, par an</div><div class="gros ${b.solde < 0 ? "neg" : b.solde > 0 ? "pos" : ""}">${fmt(b.solde)} Md€</div>
      <div class="petit">fourchette ${fmt(b.bas)} à ${fmt(b.haut)}</div></div>
      <div><div class="petit">Dette publique en 2032</div><div class="gros">${fmt(b.dette, false)} %</div><div class="petit">droit actuel : ${fmt(ref, false)} %</div></div></div>
    <h3>Vos mesures</h3>${faits.length ? `<ul>${faits.map(f => `<li>${f.lib} <b class="${f.e < 0 ? "neg" : f.e > 0 ? "pos" : ""}">${fmt(f.e)} Md€</b></li>`).join("")}</ul>` : `<p class="petit">Aucun changement : vous gardez le droit actuel.</p>`}
    <h3>Les candidats les plus proches</h3><ol>${proches.slice(0, 5).map(r => `<li><b style="color:${r.c.couleur}">${r.c.nom}</b><span class="barre-acc" style="width:${r.pct * .6}px"></span><span class="petit">${Math.round(r.pct)} % d'accord (${r.n} décisions)</span></li>`).join("")}</ol>
    <h3>Vos positions par thème</h3>${htmlAxes(choix)}
    <h3>Dépenses et impôts</h3>${carte(b)}
    <p><button id="retour">↶ Revenir à la dernière carte</button><button id="rejouer">Rejouer</button><a class="bt" href="${lien}">Ajuster dans le simulateur détaillé</a><button id="partager">Copier le lien</button></p>
    <p class="petit">Chiffrage : effet sur le solde public en 2032 par rapport au droit en vigueur, sans effet de second tour ; trajectoire : hypothèses du FMI. Données du ${D.genere}.</p></div>`;
  document.getElementById("rejouer").onclick = demarrer;
  document.getElementById("retour").onclick = annuler;
  document.getElementById("partager").onclick = () => navigator.clipboard?.writeText(new URL(lien, location.href).href);
  window.scrollTo(0, 0);
}
accueil();
</script></body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--valider", action="store_true")
    args = parser.parse_args(argv)
    if not CARTES.exists():
        print("chiffrage/cartes.yaml absent : jeu non généré")
        return 0
    erreurs = valider()
    for e in erreurs:
        print(f"ÉCHEC {e}", file=sys.stderr)
    if erreurs or args.valider:
        print(f"{len(erreurs)} erreur(s).")
        return 1 if erreurs else 0
    page = PAGE.replace("__COMMUN_JS__", COMMUN_JS).replace("__COMMUN_CSS__", COMMUN_CSS).replace("__DONNEES__", json.dumps(donnees(), ensure_ascii=False)).replace(
        "__CARTES__", json.dumps(lire_cartes(), ensure_ascii=False))
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(page, encoding="utf-8")
    print(f"-> {SORTIE.relative_to(RACINE)} ({len(lire_cartes()['cartes'])} cartes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
