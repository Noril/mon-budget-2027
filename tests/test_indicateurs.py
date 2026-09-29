"""pipelines.indicateurs.calculer sur une mini zone normalisée temporaire (hors dépôt, hors réseau)."""

import duckdb
import pytest

from pipelines import indicateurs
from pipelines.commun import ControleEchoue, lire_json


@pytest.fixture
def zone(tmp_path, monkeypatch):
    norm, sortie = tmp_path / "normalise", tmp_path / "indicateurs"
    norm.mkdir()
    duckdb.sql("SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, '2024' AS periode, 1.5 AS valeur "
               "UNION ALL SELECT 'france', 'FR', 'France', '2023', 1.0").write_parquet(str(norm / "src-a.parquet"))
    (norm / "src-a.manifeste.json").write_text('{"source": "src-a", "lignes": 2}', encoding="utf-8")
    monkeypatch.setattr(indicateurs, "NORMALISE", norm)
    monkeypatch.setattr(indicateurs, "INDICATEURS_CALCULES", sortie)
    monkeypatch.setattr(indicateurs, "RACINE", tmp_path)
    return tmp_path


def _definition(tmp_path, sql, **kw):
    (tmp_path / "f.sql").write_text(sql, encoding="utf-8")
    return {"id": "test.ind", "version": "1.0.0", "formule": "f.sql", "sources": ["src-a"], "maille": ["france"]} | kw


SQL = "SELECT maille, code, libelle, periode, valeur FROM {{source:src-a}}"


def test_calcul_nominal_ecrit_table_et_lignage(zone):
    lignage = indicateurs.calculer(_definition(zone, SQL))
    assert lignage["lignes"] == 2 and lignage["sources"]["src-a"]["source"] == "src-a"
    sortie = zone / "indicateurs"
    assert (sortie / "test.ind@1.0.0.parquet").exists()
    assert lire_json(sortie / "test.ind@1.0.0.lignage.json")["formule_sha256"] == lignage["formule_sha256"]


def test_sources_du_sql_differentes_des_sources_declarees(zone):
    with pytest.raises(ControleEchoue, match="sources du SQL"):
        indicateurs.calculer(_definition(zone, SQL, sources=["src-a", "src-b"]))


def test_source_absente_de_la_zone_normalisee(zone):
    sql = "SELECT * FROM {{source:src-b}}"
    with pytest.raises(ControleEchoue, match="absente"):
        indicateurs.calculer(_definition(zone, sql, sources=["src-b"]))


def test_colonnes_inattendues(zone):
    with pytest.raises(ControleEchoue, match="colonnes"):
        indicateurs.calculer(_definition(zone, "SELECT maille, code FROM {{source:src-a}}"))


def test_maille_hors_declaration(zone):
    with pytest.raises(ControleEchoue, match="mailles"):
        indicateurs.calculer(_definition(zone, SQL, maille=["pays"]))


def test_doublons_refuses(zone):
    sql = "SELECT * FROM {{source:src-a}} UNION ALL SELECT * FROM {{source:src-a}}"
    with pytest.raises(ControleEchoue, match="doublons"):
        indicateurs.calculer(_definition(zone, sql))


def test_main_rend_1_si_un_indicateur_echoue(monkeypatch, capsys):
    def echoue(_):
        raise ControleEchoue("x : casse")

    monkeypatch.setattr(indicateurs, "definitions_indicateurs", lambda: [(None, {"id": "x"})])
    monkeypatch.setattr(indicateurs, "calculer", echoue)
    assert indicateurs.main() == 1
    assert "ÉCHEC x : casse" in capsys.readouterr().err
