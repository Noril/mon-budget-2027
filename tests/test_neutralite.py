"""Neutralité du « candidat le plus proche » (jeu et simulateur) : qui joue comme un candidat doit le retrouver.

Le test exécute sous Node la fonction accord() réellement embarquée dans jeu.html, sur les vraies positions des
programmes. Un joueur « clone » reprend les choix d'un candidat, en change quelques-uns au hasard et répond au hasard
aux autres leviers ; le candidat imité doit sortir premier dans la quasi-totalité des parties.

Le test ne vise pas une répartition égale entre candidats : face à des réponses quelconques, un programme proche du droit
actuel ou peu détaillé ressort plus souvent, et c'est une propriété des programmes, pas du calcul.
"""

import json
import random
import shutil
import subprocess

import pytest

from outils import jeu, simulateur
from outils.chiffrage import lire_programmes

PARTIES = 300
PERTURBATIONS = 3  # leviers à choix modifiés au hasard après imitation
SEUIL = 0.95


def _parties_clones() -> tuple[list[dict], list[dict], list[dict]]:
    doc = simulateur.lire_leviers()
    leviers = doc["leviers"]
    candidats = [{"id": p["id"], "choix": simulateur.choix_candidat(doc, p["id"])} for _, p in lire_programmes()]
    hasard = random.Random(2027)
    a_choix = [l for l in leviers if l["type"] == "choix"]
    parties = []
    for c in candidats:
        for _ in range(PARTIES):
            choix = {l["id"]: hasard.choice([o["id"] for o in l["options"]]) if l["type"] == "choix"
                     else hasard.uniform(l["curseur"]["min"], l["curseur"]["max"]) for l in leviers}
            choix |= c["choix"]
            for l in hasard.sample(a_choix, PERTURBATIONS):
                choix[l["id"]] = hasard.choice([o["id"] for o in l["options"]])
            parties.append({"imite": c["id"], "choix": choix})
    return leviers, candidats, parties


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_jouer_comme_un_candidat_le_retrouve():
    leviers, candidats, parties = _parties_clones()
    script = f"""
        const D = {json.dumps({"leviers": leviers})}, C = {json.dumps(candidats)}, P = {json.dumps(parties)};
        {jeu.ACCORD_JS}
        const premiers = P.map(p => C.map(c => ({{id: c.id, pct: accord(c, p.choix).pct}})).sort((a, b) => b.pct - a.pct)[0].id);
        console.log(JSON.stringify(premiers));
    """
    premiers = json.loads(subprocess.run(["node", "-"], input=script, capture_output=True, text=True, check=True).stdout)
    taux = {c["id"]: sum(p["imite"] == c["id"] and r == c["id"] for p, r in zip(parties, premiers)) / PARTIES for c in candidats}
    faibles = {k: round(v, 3) for k, v in taux.items() if v < SEUIL}
    assert not faibles, f"candidats mal retrouvés quand on joue comme eux : {faibles}"


def test_simulateur_et_jeu_calculent_la_meme_proximite():
    """Le simulateur garde sa propre copie d'accord() : elle doit rester la même formule."""
    assert "1 - Math.abs(c.choix[l.id] - etat[l.id]) / (l.curseur.max - l.curseur.min)" in simulateur.PAGE
    assert "1 - Math.abs(c.choix[l.id] - v) / (l.curseur.max - l.curseur.min)" in jeu.ACCORD_JS
