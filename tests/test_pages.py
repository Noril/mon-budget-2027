"""Pages générées (simulateur, jeu, rapport) : validation, échappement, autonomie, accessibilité de base."""

import copy
import json
import re
import shutil
import subprocess
import textwrap

import pytest

from outils import chiffrage, jeu, simulateur
from plan import trajectoire as tr

DEPART = tr.Depart(annee=2025, dette=115.0, solde=-5.4, charge_interets=2.0, pib=2900.0)
EXTERNE = re.compile(r"""(?:src|href|action|poster)\s*=\s*["']?(?:https?:)?//|url\(\s*["']?(?:https?:)?//|@import|<link\b|<iframe|<img\b""", re.I)


@pytest.fixture(scope="module")
def donnees():
    mp = pytest.MonkeyPatch()
    mp.setattr(tr, "lire_depart", lambda: DEPART)
    yield simulateur.donnees()
    mp.undo()


@pytest.fixture(scope="module")
def pages(donnees):
    sim = simulateur.remplir(simulateur.PAGE, COMMUN_JS=simulateur.COMMUN_JS, COMMUN_CSS=simulateur.COMMUN_CSS,
                             DONNEES=simulateur.json_pour_script(donnees), GENERE=donnees["genere"])
    j = simulateur.remplir(jeu.PAGE, COMMUN_JS=simulateur.COMMUN_JS, COMMUN_CSS=simulateur.COMMUN_CSS,
                           DONNEES=simulateur.json_pour_script(donnees), CARTES=simulateur.json_pour_script(jeu.lire_cartes()))
    return {"simulateur": sim, "jeu": j}


# --- Validation ---------------------------------------------------------------------------------------


def test_simulateur_leviers_en_double():
    doc = copy.deepcopy(simulateur.lire_leviers())
    doc["leviers"].append(copy.deepcopy(doc["leviers"][0]))
    assert any("en double" in e for e in simulateur.valider(doc))


def test_simulateur_mesure_reprise_inconnue():
    doc = copy.deepcopy(simulateur.lire_leviers())
    levier = next(l for l in doc["leviers"] if l["type"] == "choix")
    levier["options"][0]["reprend"] = ["programme-fantome/mesure-fantome"]
    assert any("mesure reprise introuvable" in e for e in simulateur.valider(doc))


def test_simulateur_option_par_defaut_a_effet_nul():
    doc = copy.deepcopy(simulateur.lire_leviers())
    levier = next(l for l in doc["leviers"] if l["type"] == "choix")
    defaut = next(o for o in levier["options"] if o.get("defaut"))
    defaut["effet"] = {"central": -1.0, "bas": -2.0, "haut": 0.0}
    assert any("effet nul" in e for e in simulateur.valider(doc))


def test_simulateur_axe_inconnu():
    doc = copy.deepcopy(simulateur.lire_leviers())
    levier = next(l for l in doc["leviers"] if l["type"] == "choix")
    levier["options"][0]["axes"] = {"axe-fantome": 1}
    assert any("axe inconnu" in e for e in simulateur.valider(doc))


def test_jeu_carte_en_double_et_levier_inconnu():
    doc = copy.deepcopy(jeu.lire_cartes())
    doc["cartes"].append(copy.deepcopy(doc["cartes"][0]))
    doc["cartes"][1]["levier"] = "levier-fantome"
    erreurs = jeu.valider(doc)
    assert any("en double" in e for e in erreurs) and any("levier inconnu" in e for e in erreurs)


def test_jeu_premiere_carte_ne_peut_pas_etre_une_suite():
    doc = copy.deepcopy(jeu.lire_cartes())
    doc["cartes"][0]["suite_seulement"] = True
    assert any("première carte" in e for e in jeu.valider(doc))


def test_jeu_personnage_inconnu_et_suite_inconnue():
    doc = copy.deepcopy(jeu.lire_cartes())
    doc["cartes"][0]["personnage"] = "fantome"
    doc["cartes"][0]["gauche"]["suite"] = "carte-fantome"
    erreurs = jeu.valider(doc)
    assert any("personnage inconnu" in e for e in erreurs) and any("suite inconnue" in e for e in erreurs)


def test_jeu_cartes_reference_des_options_existantes():
    leviers = {l["id"]: l for l in simulateur.lire_leviers()["leviers"]}
    for c in jeu.lire_cartes()["cartes"]:
        assert c["levier"] in leviers


# --- Données et gabarit -------------------------------------------------------------------------------


def test_donnees_completes(donnees):
    assert len(donnees["candidats"]) >= 2 and donnees["leviers"]
    assert donnees["reference"][-1]["annee"] == 2032
    assert all(c["nom"] and c["couleur"].startswith("#") for c in donnees["candidats"])


def test_json_pour_script_neutralise_la_balise_fermante():
    brut = simulateur.json_pour_script({"x": "</script><script>alert(1)</script> & <!--"})
    assert "<" not in brut and ">" not in brut and "&" not in brut
    assert json.loads(brut)["x"].startswith("</script>")  # ...mais le JSON relu est identique


def test_remplir_ne_reinterprete_pas_les_valeurs():
    assert simulateur.remplir("a __X__ b __Y__", X="__Y__", Y="ok") == "a __Y__ b ok"
    assert simulateur.remplir("__INCONNU__", X="1") == "__INCONNU__"


def test_donnees_hostiles_ne_sortent_pas_du_script(donnees):
    d = copy.deepcopy(donnees)
    d["candidats"][0]["nom"] = "</script><img src=x onerror=alert(1)>"
    page = simulateur.remplir(simulateur.PAGE, COMMUN_JS=simulateur.COMMUN_JS, COMMUN_CSS=simulateur.COMMUN_CSS,
                              DONNEES=simulateur.json_pour_script(d), GENERE="2026-01-01")
    assert page.count("</script>") == 1 and "<img src=x" not in page


# --- Autonomie et accessibilité -----------------------------------------------------------------------


@pytest.mark.parametrize("nom", ["simulateur", "jeu"])
def test_page_autonome_et_accessible(pages, nom):
    page = pages[nom]
    assert not re.search(r"__[A-Z_]{4,}__", page), "marqueur de gabarit non remplacé"
    assert not EXTERNE.search(page), EXTERNE.search(page)
    assert not re.search(r"<script[^>]+src=", page)
    assert not re.search(r"https?://", page), "aucune URL absolue dans la page (ressource ou tracker)"
    assert page.startswith("<!doctype html>") and '<html lang="fr">' in page
    assert 'name="viewport"' in page and "maximum-scale" not in page and "user-scalable" not in page
    assert re.search(r"<title>[^<]+</title>", page)
    assert "<main" in page


def test_focus_clavier_jamais_supprime(pages):
    for page in pages.values():
        assert not re.search(r"outline\s*:\s*(none|0)", page)
    assert "prefers-color-scheme:dark" in pages["simulateur"]


def test_glossaire_atteignable_au_clavier(pages):
    assert 'class="gl" tabindex="0"' in pages["simulateur"]


def _luminance(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contraste(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.mark.parametrize("nom", ["simulateur", "jeu"])
def test_contraste_du_texte_attenue(pages, nom):
    racine = re.search(r":root\{([^}]*)\}", pages[nom]).group(1)
    v = {k: (c if len(c) == 7 else "#" + "".join(ch * 2 for ch in c[1:]))
         for k, c in re.findall(r"--([a-z]+):(#[0-9a-f]{3,6})\b", racine)}
    for fond in ("bg", "card"):
        assert _contraste(v["fg"], v[fond]) >= 7
        assert _contraste(v["muted"], v[fond]) >= 4.5, (nom, fond)
        assert _contraste(v["acc"], v[fond]) >= 4.5


def test_rapport_html_autonome_et_accessible():
    page = _rapport()
    assert '<html lang="fr">' in page and 'name="viewport"' in page and "<main>" in page
    assert not EXTERNE.search(page.replace("href='https://exemple.test/source'", ""))
    assert not re.search(r"<script", page)


# --- Échappement du rapport de chiffrage --------------------------------------------------------------


def _agregat(**mesure):
    m = {"id": "m1", "libelle": "<b>gras</b>", "domaine": "<i>d</i>", "chiffrable": True, "central": -1.0, "bas": -2.0, "haut": 0.0,
         "confiance": "haute", "url": "https://exemple.test/source", "verification": "ok", "tiers": [("<u>auteur</u>", -1.0)],
         "raison": None, "sens": None, "indicative": None, "citation": "« <script>alert(1)</script> »", "date": "2026",
         "interpretation": "<svg onload=alert(1)>", "formule": "a<b", "explication": None, "parametres": {"<x>": 1.0},
         "effets_retour": None, "commentaire_verif": "&"} | mesure
    croisiere = {"central": -1.0, "bas": -2.0, "haut": 0.0}
    an = {a: 0.0 for a in chiffrage.ANNEES}
    note = {"score": 50, "note": "BB", "composantes": {k: {"valeur": 1, "poids": 1, "detail": "<d>"} for k in
            ("couverture", "precision_promesses", "economies_documentees", "chiffrage_publie")}}
    conf = {"score": 50, "note": "BB", "composantes": {k: {"valeur": 1, "poids": 1, "detail": "<d>"} for k in
            ("confiance_mesures", "verification", "etroitesse_fourchette", "baremes_communs")}}
    return {"id": 'p"><script>', "candidat": "<script>x</script>", "parti": "<b>p</b>", "sens_non_chiffrees": {"cout": 0, "economie": 0},
            "couverture": 1.0, "indicatif": croisiere, "nb_indicatives": 0, "nb_mesures": 1, "nb_chiffrees": 1, "nb_verifiees": 1,
            "croisiere": croisiere, "couts": -1.0, "gains": 0.0, "par_annee": {"central": an, "bas": an, "haut": an},
            "annonce": {"texte": "<script>a</script>"}, "mesures": [m], "notes": {"precision": note, "confiance": conf}}


def _rapport(**mesure):
    a = _agregat(**mesure)
    serie = [{"annee": an, "dette": 100.0 + i, "solde": -3.0} for i, an in enumerate(range(2025, 2033))]
    traj = {"gel": {"reference": serie, "depart": 2025, "programmes": {a["id"]: {h: serie for h in ("central", "bas", "haut")}}}}
    return chiffrage.rapport_html([a], traj)


def test_rapport_echappe_le_contenu_des_donnees():
    page = _rapport()
    assert "<script" not in page and "<svg onload" not in page and "<b>gras" not in page and "<u>auteur" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_rapport_refuse_les_url_non_http():
    page = _rapport(url="javascript:alert(1)")
    assert "javascript:" not in page
    assert "href='#'" in page


def test_url_sure():
    assert chiffrage._url_sure("https://a.test/?q='x'") == "https://a.test/?q=&#x27;x&#x27;"
    assert chiffrage._url_sure("JavaScript:1") == "#" and chiffrage._url_sure(None) == "#"


# --- JS commun (glossaire, axes) exécuté sous Node, s'il est disponible --------------------------------


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_annoter_echappe_le_html_et_garde_les_termes():
    script = textwrap.dedent("""
        const D = {glossaire: [{terme: "TVA", definition: "<b>taxe</b> & co"}], axes: [], leviers: [], candidats: []};
    """) + simulateur.COMMUN_JS + textwrap.dedent("""
        const r = annoter("La TVA <img src=x onerror=alert(1)> & \\"q\\"");
        console.log(JSON.stringify(r));
    """)
    sortie = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    html = json.loads(sortie)
    assert "<img" not in html and "&lt;img" in html and "&amp;" in html
    assert '<span class="gl" tabindex="0">TVA<sup>?</sup><span class="def">&lt;b&gt;taxe&lt;/b&gt; &amp; co</span></span>' in html


def _contraste_blanc(hexa: str) -> float:
    """Rapport de contraste WCAG entre le texte blanc et une couleur de fond."""
    canaux = [int(hexa.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canaux)
    return 1.05 / (0.2126 * r + 0.7152 * g + 0.0722 * b + 0.05)


def test_couleurs_contraste_aa():
    """Pastilles des candidats (texte blanc) et noms des personnages (sur fond blanc) : WCAG AA, 4,5:1."""
    import yaml
    persos = yaml.safe_load((simulateur.RACINE / "chiffrage" / "cartes.yaml").read_text(encoding="utf-8"))["personnages"]
    couleurs = list(simulateur.COULEURS) + [p["couleur"] for p in persos]
    faibles = {c: round(_contraste_blanc(c), 2) for c in couleurs if _contraste_blanc(c) < 4.5}
    assert not faibles
    assert len(set(simulateur.COULEURS)) == len(simulateur.COULEURS)
