"""Cohérence des YAML de chiffrage : citations, identifiants, renvois aux barèmes."""

import re

import pytest

from outils import chiffrage

PROGRAMMES = chiffrage.lire_programmes()
BAREMES = chiffrage.lire_baremes()
IDS_BAREMES = {b["id"] for b in BAREMES}
URL = re.compile(r"^https?://\S+$")


def test_il_y_a_des_programmes_et_des_baremes():
    assert PROGRAMMES and BAREMES


def test_ids_de_baremes_uniques():
    ids = [b["id"] for b in BAREMES]
    assert len(ids) == len(set(ids))


def test_ids_de_programmes_uniques_et_egaux_au_nom_de_fichier():
    ids = [p["id"] for _, p in PROGRAMMES]
    assert len(ids) == len(set(ids))
    assert all(f.stem == p["id"] for f, p in PROGRAMMES)


@pytest.mark.parametrize("fichier,programme", PROGRAMMES, ids=lambda x: getattr(x, "stem", ""))
def test_chaque_mesure_a_citation_et_url(fichier, programme):
    for m in programme["mesures"]:
        c = m.get("citation") or {}
        assert (c.get("texte") or "").strip(), f"{fichier.name}:{m['id']} sans citation"
        assert URL.match(c.get("url") or ""), f"{fichier.name}:{m['id']} : url absente ou non http(s)"


@pytest.mark.parametrize("fichier,programme", PROGRAMMES, ids=lambda x: getattr(x, "stem", ""))
def test_ids_de_mesures_uniques(fichier, programme):
    ids = [m["id"] for m in programme["mesures"]]
    assert len(ids) == len(set(ids)), fichier.name


@pytest.mark.parametrize("fichier,programme", PROGRAMMES, ids=lambda x: getattr(x, "stem", ""))
def test_renvois_aux_baremes_et_sources_des_parametres(fichier, programme):
    for m in programme["mesures"]:
        for nom, par in (m.get("calcul") or {}).get("parametres", {}).items():
            if par.get("bareme"):
                assert par["bareme"] in IDS_BAREMES, f"{fichier.name}:{m['id']}:{nom} -> barème inconnu"
            else:
                assert par.get("source"), f"{fichier.name}:{m['id']}:{nom} sans barème ni source"


def test_mesures_non_chiffrables_disent_pourquoi():
    for _, p in PROGRAMMES:
        for m in p["mesures"]:
            if not m["chiffrable"]:
                assert m.get("raison_non_chiffrable"), f"{p['id']}:{m['id']}"


def test_valider_detecte_un_bareme_inconnu(monkeypatch):
    fichier, programme = next((f, p) for f, p in PROGRAMMES
                              if any(m.get("calcul") for m in p["mesures"]))
    programme = chiffrage._lire(fichier)
    m = next(m for m in programme["mesures"] if m.get("calcul"))
    next(iter(m["calcul"]["parametres"].values()))["bareme"] = "inexistant"
    monkeypatch.setattr(chiffrage, "lire_programmes", lambda: [(fichier, programme)])
    assert any("barème inconnu" in e for e in chiffrage.valider())


def test_valider_detecte_un_doublon_de_mesure(monkeypatch):
    fichier, _ = PROGRAMMES[0]
    programme = chiffrage._lire(fichier)
    programme["mesures"].append(dict(programme["mesures"][0]))
    monkeypatch.setattr(chiffrage, "lire_programmes", lambda: [(fichier, programme)])
    assert any("en double" in e for e in chiffrage.valider())
