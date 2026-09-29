from outils import chiffrage


def _mesure(**effet):
    base = {"central": -10.0, "bas": -12.0, "haut": -8.0,
            "montee_en_charge": {"2027": 0, "2028": 0.5, "2029": 1, "2030": 1, "2031": 1, "2032": 1}}
    return {"chiffrable": True, "effet_solde_primaire": base | effet}


def test_formule_evaluee_sur_les_parametres():
    calcul = {"formule": "-a * b", "parametres": {"a": {"valeur": 2.0}, "b": {"valeur": 5.0}}}
    assert chiffrage.evaluer(calcul) == -10.0


def test_profil_suit_la_montee_en_charge():
    assert chiffrage.profil(_mesure(), "central") == {2027: 0, 2028: -5.0, 2029: -10.0, 2030: -10.0, 2031: -10.0, 2032: -10.0}


def test_profil_annuel_explicite_et_bornes_decalees():
    m = _mesure(central=0.0, bas=-1.0, haut=0.0, annuel={"2028": -3.7, "2029": -3.7})
    assert chiffrage.profil(m, "central")[2028] == -3.7
    assert chiffrage.profil(m, "central")[2032] == 0.0
    assert chiffrage.profil(m, "bas")[2032] == -1.0


def test_depot_valide():
    assert chiffrage.valider() == []


def test_simulateur_valide():
    from outils import simulateur

    assert simulateur.valider() == []


def test_cartes_du_jeu_valides():
    from outils import jeu

    assert jeu.valider() == []
