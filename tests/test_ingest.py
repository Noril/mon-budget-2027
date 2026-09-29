from datetime import datetime, timedelta, timezone

import pytest

from pipelines import ingest
from pipelines.commun import ControleEchoue, ecrire_json

SOURCE = {"id": "s", "controles": {"colonnes": ["a", "b"], "lignes_min": 10}, "fraicheur_max_jours": 30}
MANIFESTE = {"producteur": {}}


def test_controle_nominal():
    assert ingest.controler(SOURCE, 100, {"a", "b", "c"}, MANIFESTE, 100) == []


def test_colonne_manquante_bloque():
    with pytest.raises(ControleEchoue, match="colonnes manquantes"):
        ingest.controler(SOURCE, 100, {"a"}, MANIFESTE, None)


def test_trop_peu_de_lignes_bloque():
    with pytest.raises(ControleEchoue, match="minimum attendu"):
        ingest.controler(SOURCE, 5, {"a", "b"}, MANIFESTE, None)


def test_variation_de_plus_de_20_pct_bloque():
    with pytest.raises(ControleEchoue, match="écart"):
        ingest.controler(SOURCE, 70, {"a", "b"}, MANIFESTE, 100)
    assert ingest.controler(SOURCE, 85, {"a", "b"}, MANIFESTE, 100) == []


def test_alerte_de_fraicheur():
    vieux = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    alertes = ingest.controler(SOURCE, 100, {"a", "b"}, {"producteur": {"modifie_le": vieux}}, None)
    assert alertes and "90 jours" in alertes[0]


def test_date_producteur_sans_fuseau_ne_plante_pas():
    naive = (datetime.now(timezone.utc) - timedelta(days=2)).replace(tzinfo=None).isoformat()
    assert ingest.controler(SOURCE, 100, {"a", "b"}, {"producteur": {"modifie_le": naive}}, None) == []


def test_dernier_manifeste_ignore_l_ancien_format(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "BRUT", tmp_path)
    ecrire_json(tmp_path / "s" / "20240101T000000Z" / "manifeste.json", {"fichiers": [], "recupere_le": "vieux"})
    ecrire_json(tmp_path / "s" / "20250101T000000Z" / "manifeste.json", {"ancien": True})
    assert ingest.dernier_manifeste("s")["recupere_le"] == "vieux"
    assert ingest.dernier_manifeste("inconnue") is None


def test_main_source_absente_du_catalogue(monkeypatch, capsys):
    monkeypatch.setattr(ingest, "charger_catalogue", lambda: {})
    assert ingest.main(["fantome"]) == 1
    assert "absente du catalogue" in capsys.readouterr().err
