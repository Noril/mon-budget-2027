import pytest

from outils.fiches import analyser_appel, appels, chiffres_tapes
from outils.valider import valider


def test_appel_france():
    a = analyser_appel("{{ind:sante.x@1.0.0 | france | 2025}}", "sante.x@1.0.0 | france | 2025")
    assert (a.indicateur, a.version, a.maille, a.code, a.periode) == ("sante.x", "1.0.0", "france", "FR", "2025")


def test_appel_departement():
    (a,) = appels("taux de {{ind:sante.x@2.1.0 | departement=2A | 2024}} en Corse")
    assert (a.maille, a.code, a.version) == ("departement", "2A", "2.1.0")


@pytest.mark.parametrize("contenu", ["sante.x | france | 2025", "sante.x@1.0.0 | 2025", "sante.x@1.0.0 | paris | 2025"])
def test_appel_mal_forme(contenu):
    with pytest.raises(ValueError):
        analyser_appel("{{ind:" + contenu + "}}", contenu)


def test_chiffres_tapes_detectes():
    corps = "En 2025, 4,3 % des patients ; coût de 12 M€ ; {{ind:sante.x@1.0.0 | france | 2025}} ailleurs ; 2 points."
    assert [c.strip() for c in chiffres_tapes(corps)] == ["4,3 %", "12 M€", "2 points"]


def test_annees_et_appels_acceptes():
    assert chiffres_tapes("De 2019 à 2022, voir {{ind:sante.x@1.0.0 | departement=23 | 2025}}.") == []


def test_depot_valide():
    assert valider() == []
