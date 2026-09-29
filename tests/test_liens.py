from outils.liens import citation_presente, normaliser


def test_normalisation_apostrophes_guillemets_espaces():
    assert normaliser("L’État  «  paie »\n") == "l'état paie"


def test_citation_retrouvee_malgre_cesure_pdf():
    ok, _ = citation_presente("les heures supplémentaires rapportent", "Les heures supplémen taires rapportent 1,8 Md€")
    assert ok


def test_citation_avec_coupe():
    ok, _ = citation_presente("baisser la TVA […] sur l'énergie", "Nous voulons baisser la TVA de 20 % à 5,5 % sur l'énergie.")
    assert ok


def test_citation_absente():
    ok, score = citation_presente("supprimer l'impôt sur le revenu", "Nous voulons baisser la TVA sur l'énergie.")
    assert not ok and score < 0.85
