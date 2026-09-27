import pytest

from plan.trajectoire import (
    Depart,
    HypotheseInvalide,
    ajustements_scenario,
    hypotheses_par_annee,
    projeter,
    verifier,
)

DEPART = Depart(annee=2025, dette=100.0, solde=-3.0, charge_interets=2.0, pib=1000.0)


def h(croissance=0.0, inflation=0.0, taux=0.0, solde_primaire=0.0):
    return {"croissance": croissance, "inflation": inflation, "taux": taux, "solde_primaire": solde_primaire}


def test_depart_solde_primaire():
    assert DEPART.solde_primaire == pytest.approx(-1.0)


def test_taux_egal_croissance_nominale_et_equilibre_primaire_dette_stable():
    # i = g_nominale = 2 % (croissance 2 %, inflation 0) : dette constante, solde = −intérêts
    lignes = projeter(DEPART, {2026: h(croissance=2, taux=2), 2027: h(croissance=2, taux=2)})
    assert [l["dette"] for l in lignes[1:]] == pytest.approx([100.0, 100.0])
    assert lignes[1]["charge_interets"] == pytest.approx(2 / 1.02)
    assert lignes[1]["solde"] == pytest.approx(-2 / 1.02)


def test_taux_seul_sans_croissance():
    # 10 % d'intérêts, croissance nulle, solde primaire nul : 100 -> 110 -> 121
    lignes = projeter(DEPART, {2026: h(taux=10), 2027: h(taux=10)})
    assert [l["dette"] for l in lignes] == pytest.approx([100.0, 110.0, 121.0])
    assert lignes[2]["charge_interets"] == pytest.approx(11.0)


def test_croissance_nominale_combine_volume_et_prix():
    # (1 + 1 %) × (1 + 1 %) − 1 = 2,01 % ; dette 100 / 1,0201
    (_, l) = projeter(DEPART, {2026: h(croissance=1, inflation=1)})
    assert l["dette"] == pytest.approx(100 / 1.0201)
    assert l["pib"] == pytest.approx(1000 * 1.0201)


def test_excedent_primaire_reduit_la_dette_point_pour_point():
    (_, l) = projeter(DEPART, {2026: h(solde_primaire=1)})
    assert l["dette"] == pytest.approx(99.0)
    assert l["solde"] == pytest.approx(1.0)


def test_ajustement_de_scenario_s_ajoute_au_solde_primaire():
    ref = projeter(DEPART, {2026: h(), 2027: h()})
    sce = projeter(DEPART, {2026: h(), 2027: h()}, {2026: -0.5})
    assert sce[1]["solde_primaire"] == pytest.approx(-0.5)
    assert sce[2]["dette"] - ref[2]["dette"] == pytest.approx(0.5)


def test_annees_non_consecutives_refusees():
    with pytest.raises(HypotheseInvalide):
        projeter(DEPART, {2027: h()})


def test_conversion_milliards_en_points_de_pib():
    scenario = {
        "mesures": [
            {"id": "a", "effet_solde_primaire": {"unite": "md_eur", "valeurs": {2026: -10}}},
            {"id": "b", "effet_solde_primaire": {"unite": "pts_pib", "valeurs": {2026: 0.5, 2027: 0.2}}},
        ]
    }
    assert ajustements_scenario(scenario, {2026: 2000.0, 2027: 2100.0}) == pytest.approx({2026: 0.0, 2027: 0.2})


def test_unite_inconnue_refusee():
    scenario = {"mesures": [{"id": "a", "effet_solde_primaire": {"unite": "euros", "valeurs": {2026: 1}}}]}
    with pytest.raises(HypotheseInvalide):
        ajustements_scenario(scenario, {2026: 1000.0})


DOC = {
    "annees": [2026, 2027],
    "hypotheses": [
        {"id": "croissance_reelle", "variable": "croissance", "url": "u",
         "derivation": {"type": "serie", "serie": "NGDP_RPCH"}, "valeurs": {2026: 1.0}},
        {"id": "croissance_reelle_2027", "variable": "croissance", "a_trancher": True, "convention": "reconduite",
         "derivation": {"type": "reconduction", "hypothese": "croissance_reelle", "annee": 2026}, "valeurs": {2027: 1.0}},
        {"id": "deflateur", "variable": "inflation", "url": "u",
         "derivation": {"type": "variation", "serie": "NGDP_D"}, "valeurs": {2026: 2.0, 2027: 2.0}},
        {"id": "taux_apparent", "variable": "taux", "url": "u",
         "derivation": {"type": "serie", "serie": "T"}, "valeurs": {2026: 3.0, 2027: 3.0}},
        {"id": "solde_primaire", "variable": "solde_primaire", "a_trancher": True, "convention": "gel",
         "derivation": {"type": "gel_observe"}},
    ],
}
FMI = {"NGDP_RPCH": {2026: 1.0}, "NGDP_D": {2025: 100.0, 2026: 102.0, 2027: 104.04}, "T": {2026: 3.0, 2027: 3.0}}


def test_hypotheses_conformes_a_la_source():
    assert verifier(DOC, FMI) == []


def test_hypothese_divergente_detectee():
    fmi = FMI | {"NGDP_RPCH": {2026: 1.2}}
    (erreur,) = verifier(DOC, fmi)
    assert "croissance_reelle 2026" in erreur


def test_assemblage_avec_solde_primaire_gele():
    table, a_trancher = hypotheses_par_annee(DOC, DEPART)
    assert table[2027] == {"croissance": 1.0, "inflation": 2.0, "taux": 3.0, "solde_primaire": -1.0}
    assert len(a_trancher) == 2
