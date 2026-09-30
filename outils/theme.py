"""Identité visuelle commune du site : « l'urne transparente ».

Depuis 1988, les urnes françaises sont transparentes : chacun voit les bulletins qu'elles contiennent. Le site applique
la même idée aux promesses budgétaires. Fond de plexiglas, bulletins blancs, encre d'ardoise, violet du tampon
« A voté » pour les actions.

Polices embarquées en data URI (fichiers et licences dans outils/polices/) : le site n'appelle aucune ressource externe.
- Big Shoulders Display (SIL OFL) : titres et grands nombres, lettres étroites de signalétique civique.
- Luciole (CC BY 4.0, © Laurent Bourcellier et Jonathan Perez, CTRDV) : texte courant, caractère français dessiné pour
  les personnes malvoyantes.
"""

from __future__ import annotations

import base64
import html
from functools import cache
from pathlib import Path

POLICES = Path(__file__).resolve().parent / "polices"
FACES = [
    ("Big Shoulders Display", 700, "normal", "big-shoulders-display-latin-700-normal.woff2"),
    ("Big Shoulders Display", 800, "normal", "big-shoulders-display-latin-800-normal.woff2"),
    ("Luciole", 400, "normal", "Luciole-Regular.woff2"),
    ("Luciole", 700, "normal", "Luciole-Bold.woff2"),
    ("Luciole", 400, "italic", "Luciole-Italic.woff2"),
]

# Couleurs des candidats (ordre des fichiers de programme), contraste ≥ 4,5:1 sur le blanc.
COULEURS_CANDIDATS = ["#c0392b", "#8e44ad", "#2471a3", "#117864", "#7d6608", "#a04000", "#566573", "#943126", "#1e8449", "#1f618d"]

# Directive CSP : les polices sont en data URI.
CSP_POLICES = "font-src data:"


@cache
def polices_css() -> str:
    regles = []
    for famille, graisse, style, fichier in FACES:
        b64 = base64.b64encode((POLICES / fichier).read_bytes()).decode()
        regles.append(f"@font-face{{font-family:'{famille}';font-weight:{graisse};font-style:{style};"
                      f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(regles)


# Jetons : noms repris par toutes les pages (--bg, --fg, --muted, --line, --card, --acc, --neg, --pos).
JETONS_CSS = """
:root{
  --plexi:#e3ede9;--arete:#9fbfb4;--bulletin:#ffffff;--encre:#1d2b2f;--tampon:#5a3e9b;
  --bg:var(--plexi);--fg:var(--encre);--muted:#4e6068;--line:#c3d6cf;--card:var(--bulletin);--acc:var(--tampon);
  --neg:#a8261d;--pos:#1b6a4e;--ombre:0 1px 0 #9fbfb433,0 10px 24px -14px #1d2b2f55;
  --titre:'Big Shoulders Display','Arial Narrow',sans-serif;
  --texte:'Luciole',system-ui,-apple-system,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --plexi:#0f1d1a;--arete:#3b5a51;--bulletin:#172925;--encre:#e4efeb;--tampon:#bba8f2;
  --muted:#9ab3ab;--line:#2c453e;--neg:#f0877d;--pos:#79d3ad;--ombre:0 10px 24px -14px #000c;
}}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 var(--texte);font-variant-numeric:tabular-nums}
h1,h2,h3{font-family:var(--titre);font-weight:800;line-height:1.02;letter-spacing:.005em;margin:1.6em 0 .45em}
h1{font-size:clamp(2.6rem,7vw,4.6rem)}h2{font-size:clamp(1.7rem,3.6vw,2.4rem)}h3{font-size:1.45rem}
a{color:var(--acc);text-underline-offset:.18em;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:3px solid var(--acc);outline-offset:3px;border-radius:2px}
.nav{display:flex;flex-wrap:wrap;align-items:baseline;gap:.35rem 1.4rem;max-width:72rem;margin:0 auto;padding:1rem 16px .6rem;
  border-bottom:2px solid var(--arete)}
.nav .marque{font-family:var(--titre);font-weight:800;font-size:1.55rem;color:var(--fg);text-decoration:none;margin-right:auto;
  letter-spacing:.01em}
.nav a{font-weight:700;text-decoration:none;color:var(--fg)}.nav a:hover{color:var(--acc)}
.nav a[aria-current=page]{color:var(--acc);box-shadow:inset 0 -3px 0 var(--acc)}
@media (max-width:640px){.nav{gap:.2rem 1rem;font-size:.92rem}.nav .marque{flex-basis:100%;margin-bottom:.1rem}}
.pied{max-width:72rem;margin:4rem auto 0;padding:1.2rem 16px 3rem;border-top:2px solid var(--arete);color:var(--muted);
  font-size:.92rem;display:flex;flex-wrap:wrap;gap:.4rem 1.6rem}
.pied a{color:var(--muted)}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
"""

LIENS = [("index.html", "Accueil"), ("rapport.html", "Le rapport"), ("simulateur.html", "Le simulateur"),
         ("jeu.html", "Le jeu"), ("methode.html", "Méthode et limites")]


def entete(actif: str) -> str:
    liens = "".join(f'<a href="{h}"{" aria-current=page" if h == actif else ""}>{t}</a>' for h, t in LIENS[1:])
    return f'<nav class="nav" aria-label="Sections du site"><a class="marque" href="index.html">Chiffrer 2027</a>{liens}</nav>'


def pied(genere: str) -> str:
    return (f'<footer class="pied"><span>Données du {html.escape(genere)}</span><a href="methode.html">Méthode et limites</a>'
            '<a href="mentions-legales.html">Mentions légales</a><span>Textes et chiffrages sous CC BY 4.0. Police Luciole © Laurent Bourcellier et Jonathan Perez (CC BY 4.0)</span></footer>')


def style() -> str:
    """Bloc CSS à placer en tête de chaque page, avant ses règles propres."""
    return polices_css() + JETONS_CSS
