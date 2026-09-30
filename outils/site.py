"""Assemble le site public : page d'accueil, mentions légales, et les pages générées.

    uv run python -m outils.site               # écrit build/site/

Les pages produites par outils.chiffrage, outils.simulateur et outils.jeu doivent déjà exister dans build/.
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

from outils import partage, theme

RACINE = Path(__file__).resolve().parent.parent
BUILD = RACINE / "build"
SORTIE = BUILD / "site"
PAGES = {"chiffrage.html": "rapport.html", "simulateur.html": "simulateur.html", "jeu.html": "jeu.html"}
FICHIERS = ["chiffrage.md", "tableau-de-bord.md"]
DONNEES = [RACINE / "data" / "chiffrage.json"]

# Pages autonomes : scripts et styles en ligne, aucune ressource externe.
CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; connect-src 'self'; "
       "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
VERCEL = {
    # site statique déjà construit : pas de framework ni de compilation côté Vercel (le projet détecte sinon du Python)
    "framework": None,
    "buildCommand": "",
    "installCommand": "",
    "outputDirectory": ".",
    "regions": ["cdg1"],  # fonction des statistiques exécutée à Paris, près de la base (UE)
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
main{max-width:72rem;margin:0 auto;padding:0 16px}
.prose{max-width:40rem}.prose p,.prose li{max-width:40rem}.prose li{margin:.35em 0}
.mut{color:var(--muted);font-size:.94rem}
/* Accueil */
.une{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:1rem 3rem;align-items:end;margin:3.2rem 0 2rem}
.une h1{margin:0;font-size:clamp(3rem,9vw,6.4rem);line-height:.9}
.une p{margin:0;max-width:34rem;font-size:1.08rem}
@media (max-width:760px){.une{grid-template-columns:1fr;margin-top:2rem}}
.urne{position:relative;margin:2.4rem 0 .8rem;padding:3.2rem clamp(12px,3vw,2.2rem) 2.2rem;border:2px solid var(--arete);
  border-radius:6px;background:linear-gradient(180deg,#ffffff55,#ffffff22);box-shadow:inset 0 0 0 6px #ffffff33}
@media (prefers-color-scheme:dark){.urne{background:linear-gradient(180deg,#ffffff0d,#ffffff05);box-shadow:inset 0 0 0 6px #ffffff08}}
.urne:before{content:"";position:absolute;top:-2px;left:50%;width:min(44%,18rem);height:12px;transform:translate(-50%,-50%);
  background:var(--encre);border-radius:6px;box-shadow:0 0 0 5px var(--bg)}
.bulletins{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1.4rem 1.2rem}
@media (max-width:900px){.bulletins{grid-template-columns:repeat(2,minmax(0,1fr))}}
.bulletin{display:flex}.bulletin a{flex:1;display:flex;flex-direction:column;background:var(--card);color:var(--fg);text-decoration:none;border:1px solid var(--line);
  padding:1.1rem .9rem 1rem;text-align:center;box-shadow:var(--ombre);transform:rotate(var(--r));
  transition:transform .18s ease}
.bulletin a:hover,.bulletin a:focus-visible{transform:rotate(0) translateY(-4px)}
.bulletin .nom{display:block;font-weight:700;font-size:1.02rem;line-height:1.25}
.bulletin .parti{display:block;color:var(--muted);font-size:.84rem;line-height:1.3;margin:.15rem 0 .8rem}
.bulletin .solde{display:block;margin-top:auto;font-family:var(--titre);font-weight:800;font-size:clamp(2.1rem,4.4vw,2.9rem);line-height:1;
  padding-top:.7rem;border-top:1px solid var(--line)}
.bulletin .unite{display:block;color:var(--muted);font-size:.8rem;margin-top:.2rem}
@media (prefers-reduced-motion:no-preference){
  .bulletin a{animation:tombe .7s cubic-bezier(.2,.8,.25,1) both;animation-delay:calc(var(--i) * 70ms)}
  @keyframes tombe{from{opacity:0;transform:translateY(-28px) rotate(0)}to{opacity:1;transform:rotate(var(--r))}}
}
.legende{color:var(--muted);font-size:.9rem;max-width:46rem}
.bouton{display:inline-block;font-weight:700;font-size:1.02rem;text-decoration:none;padding:.72rem 1.3rem;border-radius:4px;
  border:2px solid var(--acc);color:var(--acc);background:transparent;line-height:1.2}
.bouton:hover{background:var(--acc);color:#fff}
.bouton.plein{background:var(--acc);color:#fff}.bouton.plein:hover{background:var(--fg);border-color:var(--fg)}
@media (prefers-color-scheme:dark){.bouton:hover,.bouton.plein{color:#10201c}}
.actions{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.3rem}
.jeu{display:grid;grid-template-columns:auto minmax(0,1fr);gap:1.4rem 2.6rem;align-items:center;margin:3rem 0 0;padding:2rem clamp(16px,4vw,3rem);
  background:var(--card);border:2px solid var(--fg);border-top-width:8px;box-shadow:var(--ombre)}
@media (max-width:640px){.jeu{grid-template-columns:1fr}}
.jeu h2{margin:0 0 .4rem;font-size:clamp(2rem,5vw,3rem)}.jeu p{margin:0;max-width:36rem}
.pile{position:relative;width:132px;height:100px;margin:10px}
.pile span{position:absolute;inset:0;background:var(--card);border:1px solid var(--line);box-shadow:var(--ombre)}
.pile span:nth-child(1){transform:rotate(-8deg)}.pile span:nth-child(2){transform:rotate(5deg)}
.pile span:nth-child(3){transform:rotate(-1deg);border-top:7px solid var(--acc)}
.portes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 2.4rem;margin:3.4rem 0 1rem;border-top:2px solid var(--fg)}
@media (max-width:760px){.portes{grid-template-columns:1fr}}
.porte{padding:1.2rem 0 1.4rem;border-bottom:1px solid var(--line)}
.porte h2{margin:0 0 .35rem;font-size:2rem}.porte p{margin:0 0 1rem;color:var(--muted)}
.bandeau{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:2rem 3rem;margin-top:3rem}
@media (max-width:760px){.bandeau{grid-template-columns:1fr}}
.bandeau h2{margin-top:0}
"""


def page(titre, corps, description="", actif=""):
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(titre)}</title>
<meta name="description" content="{html.escape(description)}"><style>{theme.style()}{CSS}</style></head>
<body>{theme.entete(actif)}<main>{corps}</main>{theme.pied(date.today().isoformat())}</body></html>
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


def _md(x: float) -> str:
    if abs(x) < 0.05:
        return "0"
    s = f"{abs(x):.0f}" if abs(x) >= 10 else f"{abs(x):.1f}".replace(".", ",")
    return ("−" if x < -0.05 else "+" if x > 0.05 else "") + s


def effet_deficit(solde: float) -> tuple[str, str]:
    """Montant et libellé lisibles : un solde négatif est un déficit en plus, pas une économie."""
    if solde < -0.05:
        return _md(-solde).lstrip("+"), "Md€ de déficit en plus chaque année (2032)"
    if solde > 0.05:
        return _md(solde).lstrip("+"), "Md€ de déficit en moins chaque année (2032)"
    return "0", "sans effet net sur le déficit (2032)"


def urne() -> str:
    """Les programmes en bulletins, dans l'ordre alphabétique des noms, comme sur les panneaux électoraux."""
    fichier = RACINE / "data" / "chiffrage.json"
    if not fichier.exists():  # chiffrage pas encore calculé (tests hors chaîne de données) : urne vide
        return '<div class="urne"><ul class="bulletins"></ul></div>'
    donnees = json.loads(fichier.read_text(encoding="utf-8"))["programmes"]
    progs = sorted(donnees, key=lambda a: a["candidat"].split(" ", 1)[-1])
    items = []
    for i, a in enumerate(progs):
        c = a["croisiere"]["central"]
        signe = "neg" if c < -0.05 else "pos" if c > 0.05 else ""
        r = ((i * 37) % 7 - 3) * 0.55
        items.append(
            f'<li class="bulletin" style="--i:{i};--r:{r:.2f}deg"><a href="programme-{html.escape(a["id"])}.html">'
            f'<span class="nom">{html.escape(a["candidat"])}</span><span class="parti">{html.escape(a["parti"])}</span>'
            f'<span class="solde {signe}">{effet_deficit(c)[0]}</span><span class="unite">{effet_deficit(c)[1]}</span></a></li>')
    return f'<div class="urne"><ul class="bulletins">{"".join(items)}</ul></div>'


def accueil(cfg):
    depot = html.escape(cfg["depot"])
    return page("Mon budget 2027 : ce que coûteraient les programmes", f"""
<section class="une">
<h1>Ce que coûteraient les promesses</h1>
<p>Huit programmes pour la présidentielle de 2027, chiffrés avec la même méthode. Chaque mesure est citée mot pour
mot avec son lien, et son coût se recalcule à partir de barèmes publics. Cliquez sur un bulletin pour voir le détail.
<span class="actions"><a class="bouton plein" href="jeu.html">Jouer : construire mon programme</a></span></p>
</section>
{urne()}
<p class="legende">Ce que chaque programme ajoute au déficit public ou en retire chaque année, une fois toutes ses mesures
en place (2032). Scénario central, en milliards d'euros. Candidats dans l'ordre alphabétique. Le chiffrage ne juge pas
l'opportunité des mesures, il en donne le coût.</p>
<section class="jeu" aria-labelledby="titre-jeu">
<div class="pile" aria-hidden="true"><span></span><span></span><span></span></div>
<div><h2 id="titre-jeu">À vous de choisir</h2><p>Une trentaine de choix sur les retraites, les impôts, les fonctionnaires ou l'énergie,
à trancher à gauche ou à droite. À la fin, vous voyez votre programme, ce qu'il coûte et les candidats dont vous êtes le plus proche.</p>
<div class="actions"><a class="bouton plein" href="jeu.html">Commencer le jeu</a></div></div>
</section>
<div class="portes">
<div class="porte"><h2>Le rapport</h2><p>Chaque programme mesure par mesure, avec la citation, le calcul, les sources
et la fourchette d'incertitude.</p><a class="bouton" href="rapport.html">Lire le rapport</a></div>
<div class="porte"><h2>Le simulateur</h2><p>Les mêmes décisions, avec toutes les options. Réglez-les une à une et suivez la dette
jusqu'en 2032.</p><a class="bouton" href="simulateur.html">Composer mon budget</a></div>
</div>
<div class="bandeau">
<div class="prose"><h2>Ce que ce chiffrage mesure</h2><p>Le coût des promesses, par rapport au droit voté
au 29 septembre 2026 et hors effets de second tour : la croissance ou l'emploi invoqués par un candidat sont décrits,
pas comptés. Les chiffres sont des ordres de grandeur. <a href="methode.html">Méthode et limites</a>.</p></div>
<div class="prose"><h2>Vérifier, corriger</h2><p>Le code, les barèmes et chaque chiffrage sont publics
<a href="{depot}">sur GitHub</a>. Une citation inexacte, un calcul contestable : <a href="{depot}/issues/new/choose">signalez-le</a>{ou_ecrivez(cfg)}.
Les équipes de campagne disposent d'un <a href="mentions-legales.html">droit de réponse</a>. Données :
<a href="chiffrage.json">chiffrage (JSON)</a>, <a href="chiffrage.md">rapport (Markdown)</a>,
<a href="tableau-de-bord.md">tableau de bord</a>.</p></div>
</div>""", "Chiffrage indépendant, sourcé et rejouable des programmes de la présidentielle 2027.", "index.html")


def methode(cfg):
    d = html.escape(cfg["depot"])
    return page("Méthode et limites", f"""<div class="prose">
<h1>Méthode et limites</h1>
<h2>Principes</h2>
<ul>
<li><b>La citation d'abord.</b> Une mesure n'est retenue que si elle est citée mot pour mot, avec son lien (site du candidat ou du parti,
programme, discours, entretien publié).</li>
<li><b>Même méthode pour tous.</b> Même droit de référence (voté au 29 septembre 2026), mêmes barèmes, mêmes
conventions : deux programmes qui promettent la même chose coûtent la même chose.</li>
<li><b>Tout se vérifie.</b> Chaque formule peut être rejouée et chaque paramètre a sa source. Quand une mesure ne se
chiffre pas, c'est écrit, avec son sens probable, et la note de précision en tient compte.</li>
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
<li>La trajectoire de la dette repose sur des hypothèses macroéconomiques tirées de la base World Economic Outlook du FMI (données transformées), communes à tous.</li>
<li>Une erreur est possible. Signalez-la : elle sera corrigée, et l'historique des corrections est public.</li>
</ul>
<h2 id="production">Comment ce site est produit</h2>
<p>Ce site est produit avec des modèles d'intelligence artificielle de la famille Claude, développés par Anthropic, à
l'initiative et sous la direction d'une personne qui a fixé la méthode, les règles de neutralité et les priorités.</p>
<ul>
<li><b>Ce que l'IA a fait.</b> Rechercher et citer les mesures des programmes, trouver les sources des coûts, écrire les
calculs, vérifier chaque chiffrage par un second modèle qui ne l'avait pas écrit, rédiger les textes du site, du
simulateur et du jeu, et écrire le code.</li>
<li><b>Les garde-fous.</b> Chaque citation est comparée automatiquement au texte de sa source. Chaque montant se
recalcule par une formule publique à partir de barèmes sourcés. Les indicateurs de départ sont recalculés
indépendamment. Tout est public et rejouable.</li>
<li><b>Ce qui manque.</b> Aucun économiste n'a encore relu ces chiffrages, et les équipes de campagne n'ont pas encore
été consultées. Des erreurs sont possibles : <a href="{d}/issues/new/choose">signalez-les</a>, elles seront corrigées
publiquement.</li>
</ul>
<h2>Pour aller plus loin</h2>
<ul>
<li><a href="{d}/blob/main/chiffrage/README.md">Méthode détaillée du chiffrage</a></li>
<li><a href="{d}/blob/main/chiffrage/REFERENCE.md">Droit de référence et conventions</a></li>
<li><a href="{d}/blob/main/chiffrage/baremes.yaml">Barèmes communs et leurs sources</a></li>
<li><a href="{d}/tree/main/chiffrage/programmes">Un fichier par programme, avec les citations</a></li>
<li><a href="{d}/blob/main/plan/README.md">Trajectoire de la dette</a></li>
</ul></div>""", "Principes, conventions et limites du chiffrage.", "methode.html")


def mentions(cfg):
    e, h = cfg["editeur"], cfg["hebergeur"]
    d = html.escape(cfg["depot"])
    if e.get("nom"):
        qualite = f", {html.escape(e['qualite'])}" if e.get("qualite") else ""
        directeur = f" Directeur de la publication : {html.escape(e['directeur_publication'])}." if e.get("directeur_publication") else ""
        editeur = f"{html.escape(e['nom'])}{qualite}.{directeur}"
    else:
        editeur = f"Site publié à titre non professionnel par les contributeurs du <a href=\"{d}\">dépôt public</a>."
    return page("Mentions légales", f"""<div class="prose">
<h1>Mentions légales</h1>
<h2>Éditeur</h2>
<p>{editeur} Contact : {lien_contact(cfg)}.</p>
<h2>Hébergeur</h2>
<p>{html.escape(h['nom'])}, {html.escape(h['adresse'])}.</p>
<h2>Droit de réponse et corrections</h2>
<p>Toute personne nommée sur ce site peut demander une correction ou exercer son droit de réponse (article 6 IV de
la loi n° 2004-575 du 21 juin 2004) en écrivant au contact ci-dessus ou en ouvrant une
<a href="{d}/issues/new/choose">issue publique</a>. Une erreur factuelle démontrée (citation inexacte, attribution
erronée, lien mort, erreur de calcul) est corrigée dans les meilleurs délais. L'historique des corrections est
public dans le dépôt.</p>
<h2 id="donnees">Données personnelles</h2>
<p>Ce site ne dépose aucun cookie, n'utilise aucun traceur, aucun service d'analyse et aucune ressource externe. Les
choix faits dans le simulateur restent dans votre navigateur.</p>
<p>À la fin du jeu, vous pouvez accepter, en cochant une case décochée par défaut, que vos choix soient enregistrés
pour établir des statistiques sur chaque décision. Sont enregistrés uniquement : vos réponses aux décisions du jeu et
le jour de la partie. Ne sont enregistrés ni votre adresse IP, ni l'heure, ni aucun cookie ou identifiant : une partie
enregistrée ne peut pas être reliée à une personne. Ces données ne sont pas publiées et ne sont ni vendues ni cédées.
Elles sont hébergées dans l'Union européenne (base Postgres Neon). Les résultats des joueurs ne constituent pas un
sondage et ne sont pas représentatifs de l'opinion.</p>
<p>L'hébergeur du site peut journaliser les adresses IP des visites dans le cadre de son service ; le site ne les
conserve pas.</p>
<h2>Licences</h2>
<p>Code : MIT. Textes, chiffrages et pages : CC BY 4.0. Données : licence d'origine, indiquée dans le catalogue.
Les citations de programmes et d'articles sont reproduites à titre de courtes citations, avec leur source, à des fins
d'analyse et d'information.</p></div>""", "Éditeur, hébergeur, droit de réponse.")


DESCRIPTIONS = {
    "index.html": "Huit programmes pour la présidentielle 2027 chiffrés avec la même méthode, mesure par mesure, sources à l'appui.",
    "jeu.html": "Une trentaine de dilemmes, à gauche ou à droite. À la fin, votre programme, sa facture et les candidats qui vous ressemblent.",
    "simulateur.html": "Composez votre budget 2027 décision par décision et voyez la dette bouger jusqu'en 2032.",
    "rapport.html": "Le chiffrage des huit programmes : solde, fourchette, dette 2032, notes de précision et de confiance.",
}


def apercus(cfg) -> None:
    """Images Open Graph (build/site/og/) et balises de partage dans chaque page."""
    base = (cfg.get("url_site") or "").rstrip("/")
    og = SORTIE / "og"
    og.mkdir(exist_ok=True)
    fichier = RACINE / "data" / "chiffrage.json"
    progs = json.loads(fichier.read_text(encoding="utf-8"))["programmes"] if fichier.exists() else []
    progs = sorted(progs, key=lambda a: a["candidat"].split(" ", 1)[-1])
    images = {
        "index.html": partage.accueil([(a["candidat"].split(" ", 1)[-1], effet_deficit(a["croisiere"]["central"])[0]) for a in progs]),
        "jeu.html": partage.generique("Et vous, quel budget ?", DESCRIPTIONS["jeu.html"], pile=True),
        "simulateur.html": partage.generique("Composez votre budget 2027", DESCRIPTIONS["simulateur.html"]),
        "rapport.html": partage.generique("Les programmes 2027 chiffrés", DESCRIPTIONS["rapport.html"]),
    }
    for a in progs:
        montant, legende = effet_deficit(a["croisiere"]["central"])
        images[f"programme-{a['id']}.html"] = partage.programme(a["candidat"], a["parti"], montant, legende.replace(" (2032)", " en 2032"))
    for page in sorted(SORTIE.glob("*.html")):
        nom_image = images.get(page.name) and f"{page.stem}.png"
        if nom_image:
            (og / nom_image).write_bytes(partage.png(images[page.name]))
        image = f"{base}/og/{nom_image or 'index.png'}"
        texte = page.read_text(encoding="utf-8")
        titre = re.search(r"<title>(.*?)</title>", texte, re.S)
        titre = html.unescape(titre.group(1)) if titre else "Mon budget 2027"
        desc = DESCRIPTIONS.get(page.name)
        if not desc and page.name.startswith("programme-"):
            desc = "Chaque mesure du programme citée, chiffrée et sourcée."
        desc = desc or DESCRIPTIONS["index.html"]
        url = f"{base}/{'' if page.name == 'index.html' else page.stem}"
        balises = "".join([
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Mon budget 2027">',
            f'<meta property="og:title" content="{html.escape(titre)}"><meta property="og:description" content="{html.escape(desc)}">',
            f'<meta property="og:url" content="{html.escape(url)}"><meta property="og:image" content="{html.escape(image)}">',
            '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
            '<meta property="og:locale" content="fr_FR"><meta name="twitter:card" content="summary_large_image">',
        ])
        if 'property="og:title"' not in texte:
            page.write_text(texte.replace("</head>", balises + "</head>", 1), encoding="utf-8")


def fonctions() -> None:
    """Fonction serveur des statistiques (site/api/) et liste des valeurs autorisées, tirée des leviers du simulateur."""
    from outils.simulateur import lire_leviers

    api = SORTIE / "api"
    api.mkdir(exist_ok=True)
    for f in (RACINE / "site" / "api").glob("*.js"):
        shutil.copy(f, api / f.name)
    leviers = {}
    for l in lire_leviers()["leviers"]:
        leviers[l["id"]] = ({"options": [o["id"] for o in l["options"]]} if l["type"] == "choix"
                            else {"min": l["curseur"]["min"], "max": l["curseur"]["max"]})
    version = date.today().isoformat()
    (api / "_leviers.js").write_text(f"export const VERSION = {json.dumps(version)};\nexport const LEVIERS = "
                                     f"{json.dumps(leviers, ensure_ascii=False)};\n", encoding="utf-8")
    (SORTIE / "package.json").write_text('{"private": true, "type": "module"}\n', encoding="utf-8")


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
    for f in sorted(BUILD.glob("programme-*.html")):  # une page par programme (outils.chiffrage)
        shutil.copy(f, SORTIE / f.name)
    for f in FICHIERS:
        if (BUILD / f).exists():
            shutil.copy(BUILD / f, SORTIE / f)
    for f in DONNEES:
        if f.exists():
            shutil.copy(f, SORTIE / f.name)
    (SORTIE / "index.html").write_text(accueil(cfg), encoding="utf-8")
    (SORTIE / "methode.html").write_text(methode(cfg), encoding="utf-8")
    (SORTIE / "mentions-legales.html").write_text(mentions(cfg), encoding="utf-8")
    apercus(cfg)
    fonctions()
    (SORTIE / "vercel.json").write_text(json.dumps(VERCEL, indent=2) + "\n", encoding="utf-8")
    (SORTIE / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /api/\n", encoding="utf-8")
    print(f"-> {SORTIE.relative_to(RACINE)}/")


if __name__ == "__main__":
    main()
