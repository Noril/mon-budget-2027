"""Assemble le site public : page d'accueil, mentions légales, et les pages générées.

    uv run python -m outils.site               # écrit build/site/

Les pages produites par outils.chiffrage, outils.simulateur et outils.jeu doivent déjà exister dans build/.
"""
import html
import json
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
BUILD = RACINE / "build"
SORTIE = BUILD / "site"
PAGES = {"chiffrage.html": "rapport.html", "simulateur.html": "simulateur.html", "jeu.html": "jeu.html"}
FICHIERS = ["chiffrage.md", "tableau-de-bord.md"]
DONNEES = [RACINE / "data" / "chiffrage.json"]

# Pages autonomes : scripts et styles en ligne, aucune ressource externe.
CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
VERCEL = {
    "cleanUrls": True,
    "trailingSlash": False,
    "headers": [{"source": "/(.*)", "headers": [
        {"key": "Content-Security-Policy", "value": CSP},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "Referrer-Policy", "value": "no-referrer"},
        {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
    ]}],
}

CSS = """
:root{--bg:#fbfaf7;--fg:#1c1b19;--mut:#5e5a52;--card:#fff;--line:#e2ded4;--acc:#1f4e9c}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#eeece6;--mut:#a9a498;--card:#211f1d;--line:#37342f;--acc:#8fb4ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.55 system-ui,sans-serif}
main{max-width:52rem;margin:0 auto;padding:2rem 1rem 4rem}h1{font-size:2rem;line-height:1.2}h2{margin-top:2.2rem}
a{color:var(--acc)}.cartes{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));margin:1.5rem 0}
.carte{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem}
.carte h3{margin:.2rem 0 .4rem}.carte a{font-weight:600}.mut{color:var(--mut);font-size:.92rem}
footer{border-top:1px solid var(--line);margin-top:3rem;padding-top:1rem;color:var(--mut);font-size:.92rem}
a:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
"""


def page(titre, corps, description=""):
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(titre)}</title>
<meta name="description" content="{html.escape(description)}"><style>{CSS}</style></head>
<body><main>{corps}
<footer><a href="index.html">Accueil</a> · <a href="mentions-legales.html">Mentions légales</a> ·
<a href="methode.html">Méthode et limites</a></footer></main></body></html>
"""


def charger_config():
    """Lit site/site.yaml ; les champs d'édition sont facultatifs, le contact par défaut est le suivi d'issues."""
    cfg = yaml.safe_load((RACINE / "site" / "site.yaml").read_text(encoding="utf-8"))
    cfg["editeur"] = cfg.get("editeur") or {}
    return cfg


def lien_contact(cfg):
    """Adresse de contact si elle est renseignée, sinon le formulaire d'issues du dépôt."""
    if cfg.get("contact"):
        c = html.escape(cfg["contact"])
        return f'<a href="mailto:{c}">{c}</a>'
    return f'<a href="{html.escape(cfg["depot"])}/issues/new/choose">le formulaire d\'issues du dépôt</a>'


def ou_ecrivez(cfg):
    if not cfg.get("contact"):
        return ""
    c = html.escape(cfg["contact"])
    return f' ou écrivez à <a href="mailto:{c}">{c}</a>'


def accueil(cfg):
    depot = cfg["depot"]
    return page("Chiffrer les programmes 2027", f"""
<h1>Chiffrer les programmes 2027, en open data</h1>
<p>Un chiffrage indépendant et rejouable des programmes des candidats à l'élection présidentielle de 2027 :
chaque mesure est citée mot pour mot avec son lien, son coût se recalcule à partir de barèmes publics communs, et
l'effet cumulé est projeté sur la dette publique jusqu'en 2032. Même méthode pour tous les candidats, aucun jugement
sur l'opportunité des mesures.</p>
<div class="cartes">
<div class="carte"><h3>Le rapport</h3><p>Coût de chaque programme, mesure par mesure, avec les sources et les
incertitudes.</p><a href="rapport.html">Lire le rapport</a></div>
<div class="carte"><h3>Le simulateur</h3><p>Composez votre propre budget et situez-le par rapport aux
candidats.</p><a href="simulateur.html">Ouvrir le simulateur</a></div>
<div class="carte"><h3>Le jeu du budget</h3><p>Des choix, deux options, l'effet sur le solde et la
dette.</p><a href="jeu.html">Jouer</a></div>
</div>
<p class="mut">Le chiffrage ne prédit pas le résultat d'une politique : il calcule ce que coûterait ce qui est promis,
au droit voté au 29 septembre 2026, sans effet de second tour (croissance, emploi). Lisez la
<a href="methode.html">méthode et ses limites</a>.</p>
<h2>Vérifier et contribuer</h2>
<p>Tout est public : le code (licence MIT), les textes et chiffrages (CC BY 4.0) et les données (licence d'origine)
sont sur <a href="{html.escape(depot)}">GitHub</a>. Une erreur, une citation inexacte, un barème contestable :
<a href="{html.escape(depot)}/issues/new/choose">ouvrez une issue</a>{ou_ecrivez(cfg)}. Les candidats et leurs équipes
disposent d'un droit de réponse : voir les <a href="mentions-legales.html">mentions légales</a>.</p>
<p class="mut">Généré le {date.today().isoformat()}. Téléchargements :
<a href="chiffrage.md">rapport (Markdown)</a> · <a href="tableau-de-bord.md">tableau de bord</a> ·
<a href="chiffrage.json">données du chiffrage (JSON)</a>.</p>""",
                "Chiffrage indépendant, sourcé et rejouable des programmes de la présidentielle 2027.")


def methode(cfg):
    d = html.escape(cfg["depot"])
    return page("Méthode et limites", f"""
<h1>Méthode et limites</h1>
<h2>Principes</h2>
<ul>
<li><b>Citation d'abord.</b> Une mesure n'entre que citée mot pour mot, avec son URL (site du candidat ou du parti,
programme, discours, entretien publié).</li>
<li><b>Même méthode pour tous.</b> Même droit de référence (voté au 29 septembre 2026), mêmes barèmes, mêmes
conventions : deux programmes qui promettent la même chose coûtent la même chose.</li>
<li><b>Rien d'invérifiable.</b> Formules rejouables, paramètres sourcés. Ce qui ne se chiffre pas est dit, avec son
sens probable, et mesuré par une note de précision.</li>
<li><b>Aucun effet de second tour</b> dans le solde : la croissance, l'emploi ou les taux invoqués par les
candidats sont décrits, pas comptés.</li>
<li><b>Neutralité.</b> Le chiffrage ne juge pas l'opportunité des mesures.</li>
</ul>
<h2>Limites</h2>
<ul>
<li>Les programmes ne sont pas tous définitifs : certains candidats ne sont pas officiellement déclarés, et les
sources sont des déclarations publiques, pas un programme unique et stable.</li>
<li>Les chiffres sont des ordres de grandeur, au droit constant, avec des barèmes moyens. Une promesse vague est
chiffrée selon sa lecture la plus probable, qui est écrite.</li>
<li>La trajectoire de la dette repose sur des hypothèses macroéconomiques du FMI, communes à tous.</li>
<li>Une erreur est possible : signalez-la, elle sera corrigée et l'historique des corrections est public.</li>
</ul>
<h2>Pour aller plus loin</h2>
<ul>
<li><a href="{d}/blob/main/chiffrage/README.md">Méthode détaillée du chiffrage</a></li>
<li><a href="{d}/blob/main/chiffrage/REFERENCE.md">Droit de référence et conventions</a></li>
<li><a href="{d}/blob/main/chiffrage/baremes.yaml">Barèmes communs et leurs sources</a></li>
<li><a href="{d}/tree/main/chiffrage/programmes">Un fichier par programme, avec les citations</a></li>
<li><a href="{d}/blob/main/plan/README.md">Trajectoire de la dette</a></li>
</ul>""", "Principes, conventions et limites du chiffrage.")


def mentions(cfg):
    e, h = cfg["editeur"], cfg["hebergeur"]
    d = html.escape(cfg["depot"])
    if e.get("nom"):
        qualite = f", {html.escape(e['qualite'])}" if e.get("qualite") else ""
        directeur = f" Directeur de la publication : {html.escape(e['directeur_publication'])}." if e.get("directeur_publication") else ""
        editeur = f"{html.escape(e['nom'])}{qualite}.{directeur}"
    else:
        editeur = f"Site publié à titre non professionnel par les contributeurs du <a href=\"{d}\">dépôt public</a>."
    return page("Mentions légales", f"""
<h1>Mentions légales</h1>
<h2>Éditeur</h2>
<p>{editeur} Contact : {lien_contact(cfg)}.</p>
<h2>Hébergeur</h2>
<p>{html.escape(h['nom'])}, {html.escape(h['adresse'])}.</p>
<h2>Droit de réponse et corrections</h2>
<p>Toute personne nommée sur ce site peut demander une correction ou exercer son droit de réponse (article 6 IV de
la loi n° 2004-575 du 21 juin 2004) en écrivant à le contact ci-dessus ou en ouvrant une
<a href="{d}/issues/new/choose">issue publique</a>. Une erreur factuelle démontrée (citation inexacte, attribution
erronée, lien mort, erreur de calcul) est corrigée dans les meilleurs délais ; l'historique des corrections est
public dans le dépôt.</p>
<h2>Données personnelles</h2>
<p>Ce site est statique : il ne dépose aucun cookie, n'utilise aucun traceur, aucun service d'analyse et aucune
ressource externe. Les choix saisis dans le simulateur et le jeu restent dans votre navigateur. L'hébergeur peut
journaliser les adresses IP des visites dans le cadre de son service.</p>
<h2>Licences</h2>
<p>Code : MIT. Textes, chiffrages et pages : CC BY 4.0. Données : licence d'origine, indiquée dans le catalogue.
Les citations de programmes et d'articles sont reproduites à titre de courtes citations, avec leur source, à des fins
d'analyse et d'information.</p>""", "Éditeur, hébergeur, droit de réponse.")


def main():
    cfg = charger_config()
    absents = [f for f in PAGES if not (BUILD / f).exists()]
    if absents:
        sys.exit("pages manquantes dans build/ : " + ", ".join(absents) + " (lancer outils.chiffrage, simulateur, jeu)")
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir(parents=True)
    for source, cible in PAGES.items():
        shutil.copy(BUILD / source, SORTIE / cible)
    for f in FICHIERS:
        if (BUILD / f).exists():
            shutil.copy(BUILD / f, SORTIE / f)
    for f in DONNEES:
        if f.exists():
            shutil.copy(f, SORTIE / f.name)
    (SORTIE / "index.html").write_text(accueil(cfg), encoding="utf-8")
    (SORTIE / "methode.html").write_text(methode(cfg), encoding="utf-8")
    (SORTIE / "mentions-legales.html").write_text(mentions(cfg), encoding="utf-8")
    (SORTIE / "vercel.json").write_text(json.dumps(VERCEL, indent=2) + "\n", encoding="utf-8")
    (SORTIE / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    print(f"-> {SORTIE.relative_to(RACINE)}/")


if __name__ == "__main__":
    main()
