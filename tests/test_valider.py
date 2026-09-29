import copy

from outils import valider
from pipelines import commun


def test_main_ok_sur_le_depot(capsys):
    assert valider.main() == 0
    assert "Dépôt valide" in capsys.readouterr().out


def test_source_en_double_signalee(monkeypatch):
    src = [(commun.RACINE / "catalogue" / "x.yaml", {"id": "dup"}), (commun.RACINE / "catalogue" / "y.yaml", {"id": "dup"})]
    monkeypatch.setattr(valider, "sources_du_catalogue", lambda: src)
    erreurs = valider.valider()
    assert any("« dup » déclarée plusieurs fois" in e for e in erreurs)


def test_source_active_sans_connecteur(monkeypatch):
    reelle = commun.sources_du_catalogue()
    fichier, source = reelle[0]
    source = copy.deepcopy(source)
    source["statut"] = "actif"
    source["acces"] = dict(source["acces"], mode="inexistant")
    monkeypatch.setattr(valider, "sources_du_catalogue", lambda: [(fichier, source)])
    assert any("sans connecteur" in e for e in valider.valider())


def test_indicateur_avec_source_inconnue(monkeypatch):
    chemin, d = commun.definitions_indicateurs()[0]
    d = copy.deepcopy(d)
    d["sources"] = ["source-fantome"]
    monkeypatch.setattr(valider, "definitions_indicateurs", lambda: [(chemin, d)])
    assert any("source inconnue du catalogue « source-fantome »" in e for e in valider.valider())


def test_indicateur_avec_formule_introuvable(monkeypatch):
    chemin, d = commun.definitions_indicateurs()[0]
    d = copy.deepcopy(d)
    d["formule"] = "indicateurs/nexiste/pas.sql"
    monkeypatch.setattr(valider, "definitions_indicateurs", lambda: [(chemin, d)])
    assert any("formule introuvable" in e for e in valider.valider())


def test_main_renvoie_1_en_cas_d_erreur(monkeypatch, capsys):
    monkeypatch.setattr(valider, "valider", lambda: ["boum"])
    assert valider.main() == 1
    assert "ERREUR boum" in capsys.readouterr().err
