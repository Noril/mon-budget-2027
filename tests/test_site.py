import pytest

from outils import site


def test_config_incomplete_refusee_sans_brouillon():
    with pytest.raises(SystemExit):
        site.charger_config(brouillon=False)


def test_config_brouillon_marque_les_champs_a_completer():
    cfg = site.charger_config(brouillon=True)
    assert cfg["contact"] == "(à compléter)"
    assert "à compléter" in site.mentions(cfg)


def test_pages_echappent_le_html():
    cfg = site.charger_config(brouillon=True)
    cfg["editeur"]["nom"] = "<script>x</script>"
    assert "<script>x" not in site.mentions(cfg)
