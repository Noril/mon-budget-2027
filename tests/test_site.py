from outils import site


def test_config_vide_renvoie_au_depot():
    cfg = site.charger_config()
    assert "issues/new/choose" in site.lien_contact(cfg)
    assert "issues/new/choose" in site.mentions(cfg)
    assert "à compléter" not in site.mentions(cfg)


def test_contact_et_editeur_renseignes():
    cfg = site.charger_config()
    cfg["contact"] = "a@b.fr"
    cfg["editeur"] = {"nom": "Jeanne", "qualite": "personne physique"}
    m = site.mentions(cfg)
    assert "mailto:a@b.fr" in m and "Jeanne, personne physique" in m


def test_pages_echappent_le_html():
    cfg = site.charger_config()
    cfg["editeur"] = {"nom": "<script>x</script>"}
    cfg["contact"] = "<i>@x"
    assert "<script>x" not in site.mentions(cfg)
    assert "<i>@x" not in site.accueil(cfg)
