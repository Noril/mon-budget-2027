import json

import pytest
import yaml

from pipelines import commun


def test_sha256_est_stable(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"abc")
    assert commun.sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_json_aller_retour_avec_accents(tmp_path):
    f = tmp_path / "sous" / "x.json"
    commun.ecrire_json(f, {"é": "à"})
    assert commun.lire_json(f) == {"é": "à"}
    assert "é" in f.read_text(encoding="utf-8")  # ensure_ascii=False


def test_maintenant_format_iso_utc():
    assert commun.maintenant().endswith("Z") and len(commun.maintenant()) == 20


def test_commit_courant_sans_git(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(commun.subprocess, "run", boom)
    assert commun.commit_courant() is None


def test_catalogue_lit_les_yaml(tmp_path, monkeypatch):
    (tmp_path / "a.yaml").write_text(yaml.safe_dump([{"id": "s1"}, {"id": "s2"}]), encoding="utf-8")
    (tmp_path / "b.yaml").write_text(yaml.safe_dump([{"id": "s1"}]), encoding="utf-8")
    (tmp_path / "vide.yaml").write_text("", encoding="utf-8")
    monkeypatch.setattr(commun, "CATALOGUE", tmp_path)
    assert [s["id"] for _, s in commun.sources_du_catalogue()] == ["s1", "s2", "s1"]  # doublons gardés pour valider
    assert set(commun.charger_catalogue()) == {"s1", "s2"}


def test_catalogue_du_depot_a_des_ids_uniques():
    ids = [s["id"] for _, s in commun.sources_du_catalogue()]
    assert ids and len(ids) == len(set(ids))


def test_definitions_indicateurs_du_depot():
    defs = [d for _, d in commun.definitions_indicateurs()]
    assert defs and all({"id", "version"} <= set(d) for d in defs)


def test_controle_echoue_est_une_exception():
    with pytest.raises(commun.ControleEchoue):
        raise commun.ControleEchoue("x")
    assert json.dumps({"ok": True})
