"""Neutralité du « candidat le plus proche » (jeu et simulateur) : qui joue comme un candidat doit le retrouver.

Le test exécute sous Node la fonction accord() réellement embarquée dans jeu.html, sur les vraies positions des
programmes. Un joueur « clone » reprend les choix d'un candidat, en change quelques-uns au hasard et répond au hasard
aux autres leviers ; le candidat imité doit sortir premier dans la quasi-totalité des parties.

La propriété est vérifiée pour le jeu complet, pour des combinaisons de thèmes tirées au hasard (au moins
MIN_QUESTIONS_PARTIE questions) et avec des thèmes étoilés. Le test ne vise pas une répartition égale entre candidats :
face à des réponses quelconques, un programme proche du droit actuel ou peu détaillé ressort plus souvent, et c'est une
propriété des programmes, pas du calcul.
"""

import json
import random
import shutil
import subprocess

import pytest

from outils import jeu, simulateur
from outils.chiffrage import lire_programmes

PARTIES = 200
PERTURBATIONS = 2  # leviers à choix joués modifiés au hasard après imitation
SEUIL = 0.95
SEUIL_THEMES = 0.85  # avec peu de thèmes, deux programmes peuvent coïncider sur toutes les questions jouées


def _contexte():
    doc = simulateur.lire_leviers()
    candidats = [{"id": p["id"], "choix": simulateur.choix_candidat(doc, p["id"])} for _, p in lire_programmes()]
    return doc["leviers"], candidats, jeu.lire_cartes()["themes"]


def _clone(c, leviers, joues, hasard):
    """Partie d'un joueur qui imite le candidat c sur les leviers joués."""
    choix = {}
    for l in leviers:
        if l["id"] not in joues:
            continue
        choix[l["id"]] = (hasard.choice([o["id"] for o in l["options"]]) if l["type"] == "choix"
                          else hasard.uniform(l["curseur"]["min"], l["curseur"]["max"]))
        if l["id"] in c["choix"]:
            choix[l["id"]] = c["choix"][l["id"]]
    a_choix = [l for l in leviers if l["type"] == "choix" and l["id"] in joues]
    for l in hasard.sample(a_choix, min(PERTURBATIONS, len(a_choix))):
        choix[l["id"]] = hasard.choice([o["id"] for o in l["options"]])
    return choix


def _premiers(leviers, candidats, parties):
    script = f"""
        const D = {json.dumps({"leviers": leviers})}, C = {json.dumps(candidats)}, P = {json.dumps(parties)};
        {jeu.ACCORD_JS}
        const premiers = P.map(p => {{
          const r = C.map(c => ({{id: c.id, ...accord(c, p.choix, p.poids)}})).filter(r => r.n >= p.min);
          r.sort((a, b) => b.pct - a.pct);
          return r.length && (r.length < 2 || r[0].pct > r[1].pct) ? r[0].id : null;  // égalité en tête : non retrouvé
        }});
        console.log(JSON.stringify(premiers));
    """
    sortie = subprocess.run(["node", "-"], input=script, capture_output=True, text=True, check=True).stdout
    return json.loads(sortie)


def _taux(parties, premiers):
    total, bons = {}, {}
    for p, r in zip(parties, premiers):
        total[p["imite"]] = total.get(p["imite"], 0) + 1
        bons[p["imite"]] = bons.get(p["imite"], 0) + (r == p["imite"])
    return {k: bons[k] / total[k] for k in total}


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_jouer_comme_un_candidat_le_retrouve():
    leviers, candidats, _ = _contexte()
    hasard = random.Random(2027)
    tous = {l["id"] for l in leviers}
    parties = [{"imite": c["id"], "choix": _clone(c, leviers, tous, hasard), "poids": None, "min": 1}
               for c in candidats for _ in range(PARTIES)]
    faibles = {k: round(v, 3) for k, v in _taux(parties, _premiers(leviers, candidats, parties)).items() if v < SEUIL}
    assert not faibles, f"candidats mal retrouvés quand on joue comme eux : {faibles}"


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_jouer_comme_un_candidat_sur_quelques_themes_le_retrouve():
    """Thèmes tirés au hasard (au moins MIN_QUESTIONS_PARTIE questions), certains étoilés : poids comme dans le jeu."""
    leviers, candidats, themes = _contexte()
    hasard = random.Random(1789)
    parties = []
    for c in candidats:
        for _ in range(PARTIES):
            while True:
                pris = [t for t in themes if hasard.random() < 0.5]
                joues = {l for t in pris for l in t["leviers"]}
                positions = sum(l in c["choix"] for l in joues)
                if len(joues) >= jeu.MIN_QUESTIONS_PARTIE and positions >= jeu.MIN_POSITIONS:
                    break
            etoiles = {t["id"] for t in pris if hasard.random() < 0.3}
            poids = {l: jeu.POIDS_FAVORI if t["id"] in etoiles else 1 for t in pris for l in t["leviers"]}
            parties.append({"imite": c["id"], "choix": _clone(c, leviers, joues, hasard), "poids": poids,
                            "min": jeu.MIN_POSITIONS})
    faibles = {k: round(v, 3) for k, v in _taux(parties, _premiers(leviers, candidats, parties)).items() if v < SEUIL_THEMES}
    assert not faibles, f"candidats mal retrouvés sur une sélection de thèmes : {faibles}"


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_levier_non_joue_ne_compte_pas():
    leviers, candidats, _ = _contexte()
    c = next(c for c in candidats if len(c["choix"]) > 3)
    un = next(iter(c["choix"]))
    parties = [{"imite": c["id"], "choix": {un: c["choix"][un]}, "poids": {un: 1}, "min": 1}]
    script = f"""
        const D = {json.dumps({"leviers": leviers})};
        {jeu.ACCORD_JS}
        console.log(JSON.stringify(accord({json.dumps(c)}, {json.dumps(parties[0]["choix"])}, {json.dumps(parties[0]["poids"])})));
    """
    r = json.loads(subprocess.run(["node", "-"], input=script, capture_output=True, text=True, check=True).stdout)
    assert r == {"pct": 100, "n": 1}


def test_simulateur_et_jeu_calculent_la_meme_proximite():
    """Le simulateur garde sa propre boucle accord() (sans poids) mais la même fonction d'écart que le jeu."""
    assert "__ECART_JS__" in simulateur.PAGE and "s += 1 - ecart(l, c.choix[l.id], etat[l.id]);" in simulateur.PAGE
    assert jeu.ACCORD_JS.startswith(simulateur.ECART_JS) and "s += w * (1 - ecart(l, c.choix[l.id], v));" in jeu.ACCORD_JS


def _node(script):
    return json.loads(subprocess.run(["node", "-"], input=script, capture_output=True, text=True, check=True).stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_ecart_par_paliers():
    """Option voisine : demi-désaccord ; deux crans ou plus : désaccord entier ; levier à deux options : tout ou rien ;
    curseur proportionnel."""
    l = {"type": "choix", "options": [{"id": x} for x in "abcde"]}
    deux = {"type": "choix", "options": [{"id": x} for x in "ab"]}
    trois = {"type": "choix", "options": [{"id": x} for x in "abc"]}
    cur = {"type": "curseur", "curseur": {"min": -10, "max": 10}}
    r = _node(f"""{simulateur.ECART_JS}
        const l = {json.dumps(l)}, deux = {json.dumps(deux)}, trois = {json.dumps(trois)}, cur = {json.dumps(cur)};
        console.log(JSON.stringify([ecart(l, "a", "a"), ecart(l, "a", "b"), ecart(l, "d", "c"), ecart(l, "b", "d"),
          ecart(l, "a", "e"), ecart(l, "a", "inconnue"), ecart(l, "x", "x"), ecart(deux, "a", "b"),
          ecart(trois, "a", "b"), ecart(trois, "a", "c"), ecart(cur, -10, 10), ecart(cur, 0, 5)]));""")
    assert r == [0, 0.5, 0.5, 1, 1, 1, 0, 1, 0.5, 1, 1, 0.25]


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_desaccord_oppose_eloigne_plus_qu_un_cran():
    """Le cas qui motive le calcul : même nombre d'accords exacts, mais l'un est à l'opposé sur le reste et l'autre à
    un cran ; le second doit être plus proche."""
    leviers = [{"id": f"l{i}", "type": "choix", "options": [{"id": x, "defaut": x == "c"} for x in "abcde"]}
               for i in range(4)]
    joueur = {"l0": "a", "l1": "a", "l2": "a", "l3": "a"}
    oppose = {"id": "oppose", "choix": {"l0": "a", "l1": "a", "l2": "e", "l3": "e"}}
    voisin = {"id": "voisin", "choix": {"l0": "a", "l1": "a", "l2": "b", "l3": "b"}}
    r = _node(f"""const D = {json.dumps({"leviers": leviers})};
        {jeu.ACCORD_JS}
        console.log(JSON.stringify([accord({json.dumps(oppose)}, {json.dumps(joueur)}), accord({json.dumps(voisin)}, {json.dumps(joueur)})]));""")
    assert r[0] == {"pct": 50, "n": 4} and r[1] == {"pct": 75, "n": 4}


def test_validateur_refuse_des_options_non_rangees():
    doc = simulateur.lire_leviers()
    l = next(l for l in doc["leviers"] if l["type"] == "choix" and len(l["options"]) >= 3)
    l["options"][0], l["options"][1] = l["options"][1], l["options"][0]
    if l["options"][0]["effet"]["central"] == l["options"][1]["effet"]["central"]:
        pytest.skip("deux premières options de même effet")
    assert any(e.startswith(f"simulateur.yaml:{l['id']} : options à ranger") for e in simulateur.valider(doc))


def test_toute_position_de_candidat_a_une_carte():
    """Chaque option tenue par un candidat est proposée par une carte, principale ou « suite »."""
    cartes = jeu.lire_cartes()["cartes"]
    proposees = {(c["levier"], c[cote].get("option", c[cote].get("valeur"))) for c in cartes for cote in ("gauche", "droite")}
    leviers, candidats, _ = _contexte()
    a_choix = {l["id"] for l in leviers if l["type"] == "choix"}
    manquantes = [(c["id"], l, v) for c in candidats for l, v in c["choix"].items() if l in a_choix and (l, v) not in proposees]
    assert not manquantes, f"positions de candidats sans carte : {manquantes}"


def _jouer_carte_par_carte(cand, cartes, racines, hasard):
    """Partie jouée carte par carte, dans un ordre aléatoire, par un joueur qui vise les positions du candidat :
    à chaque carte, il prend le côté qui donne ou mène (par les suites) à la position visée ; sinon au hasard.
    Même mécanique que jeu.html : une carte « suite » s'intercale juste après sa carte mère."""
    par_id = {c["id"]: c for c in cartes}
    val = lambda c, x: c[x].get("option", c[x].get("valeur"))  # noqa: E731

    def mene(c, cote, cible):
        vus, pile = set(), [c[cote].get("suite")]
        while pile:
            i = pile.pop()
            if not i or i in vus:
                continue
            vus.add(i)
            cc = par_id[i]
            if cible in (val(cc, "gauche"), val(cc, "droite")):
                return True
            pile += [cc["gauche"].get("suite"), cc["droite"].get("suite")]
        return False

    choix, file = {}, hasard.sample(racines, len(racines))
    while file:
        c = par_id[file.pop(0)]
        cible = cand["choix"].get(c["levier"], object())
        if val(c, "droite") == cible or (val(c, "gauche") != cible and mene(c, "droite", cible)):
            cote = "droite"
        elif val(c, "gauche") == cible or mene(c, "gauche", cible):
            cote = "gauche"
        else:
            cote = hasard.choice(["gauche", "droite"])
        choix[c["levier"]] = val(c, cote)
        if s := c[cote].get("suite"):
            file.insert(0, s)
    return choix


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_jouer_carte_par_carte_comme_un_candidat_le_retrouve():
    """Le test qui aurait révélé le biais d'un plafond de cartes : il passe par l'enchaînement réel des cartes et des
    suites, et pas seulement par des choix tout faits. Tous thèmes inclus, puis une sélection de thèmes."""
    leviers, candidats, themes = _contexte()
    cartes = jeu.lire_cartes()["cartes"]
    hasard = random.Random(14)
    parties = []
    for c in candidats:
        for k in range(60):
            pris = themes if k % 2 == 0 else [t for t in themes if hasard.random() < 0.6]
            joues = {l for t in pris for l in t["leviers"]}
            if len(joues) < jeu.MIN_QUESTIONS_PARTIE or sum(l in c["choix"] for l in joues) < jeu.MIN_POSITIONS:
                pris, joues = themes, {l for t in themes for l in t["leviers"]}
            racines = [x["id"] for x in cartes if not x.get("suite_seulement") and x["levier"] in joues]
            choix = _jouer_carte_par_carte(c, cartes, racines, hasard)
            parties.append({"imite": c["id"], "choix": choix, "poids": {l: 1 for l in choix}, "min": jeu.MIN_POSITIONS})
    faibles = {k: round(v, 3) for k, v in _taux(parties, _premiers(leviers, candidats, parties)).items() if v < SEUIL}
    assert not faibles, f"candidats mal retrouvés en jouant carte par carte : {faibles}"
