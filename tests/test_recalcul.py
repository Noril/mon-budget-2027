from outils.recalcul import comparer


def test_aucun_ecart_sur_tables_identiques():
    table = {("france", "FR", "2024"): 4.9, ("region", "11", "2024"): 6.0}
    ecarts = comparer(table, dict(table))
    assert ecarts["seulement_dans_attendu"] == []
    assert ecarts["seulement_dans_recalcule"] == []
    assert ecarts["valeurs_differentes"] == []
    assert ecarts["lignes_comparees"] == 2


def test_ecart_tolere_sous_le_seuil():
    attendu = {("france", "FR", "2024"): 4.9}
    recalcule = {("france", "FR", "2024"): 4.9 + 1e-9}
    ecarts = comparer(attendu, recalcule)
    assert ecarts["valeurs_differentes"] == []


def test_valeur_differente_detectee():
    attendu = {("france", "FR", "2024"): 4.9}
    recalcule = {("france", "FR", "2024"): 5.2}
    ecarts = comparer(attendu, recalcule)
    assert len(ecarts["valeurs_differentes"]) == 1
    d = ecarts["valeurs_differentes"][0]
    assert (d["maille"], d["code"], d["periode"], d["attendu"], d["recalcule"]) == ("france", "FR", "2024", 4.9, 5.2)


def test_ligne_absente_d_un_cote_detectee():
    attendu = {("france", "FR", "2024"): 4.9, ("departement", "75", "2024"): 3.1}
    recalcule = {("france", "FR", "2024"): 4.9, ("departement", "76", "2024"): 2.2}
    ecarts = comparer(attendu, recalcule)
    assert ecarts["seulement_dans_attendu"] == [{"maille": "departement", "code": "75", "periode": "2024"}]
    assert ecarts["seulement_dans_recalcule"] == [{"maille": "departement", "code": "76", "periode": "2024"}]
