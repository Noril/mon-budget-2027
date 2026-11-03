from outils import site


def test_config_vide_renvoie_au_depot():
    cfg = site.charger_config() | {"contact": ""}
    assert "issues/new/choose" in site.lien_contact(cfg)
    assert "issues/new/choose" in site.mentions(cfg)
    assert "à compléter" not in site.mentions(cfg)


def test_contact_et_editeur_renseignes():
    cfg = site.charger_config()
    cfg["contact"] = "a@b.fr"
    cfg["editeur"] = {"nom": "Jeanne", "qualite": "personne physique"}
    m = site.mentions(cfg)
    assert "mailto:a@b.fr" in m and "Jeanne, personne physique" in m


def test_contact_du_site_publie():
    cfg = site.charger_config()
    assert cfg["contact"] == "mon-budget-2027@proton.me"
    assert "mailto:mon-budget-2027@proton.me" in site.mentions(cfg)


def test_pages_echappent_le_html():
    cfg = site.charger_config()
    cfg["editeur"] = {"nom": "<script>x</script>"}
    cfg["contact"] = "<i>@x"
    assert "<script>x" not in site.mentions(cfg)
    assert "<i>@x" not in site.accueil(cfg)


def test_vercel_json_impose_csp_sans_ressource_externe():
    csp = next(h["value"] for h in site.VERCEL["headers"][0]["headers"] if h["key"] == "Content-Security-Policy")
    assert "default-src 'none'" in csp and "http" not in csp
    assert site.VERCEL["cleanUrls"] is True


def test_apercus_de_partage(tmp_path, monkeypatch):
    from outils import partage

    im = partage.generique("Titre", "Texte de description")
    assert im.size == (1200, 630) and partage.png(im).startswith(b"\x89PNG")


def test_modeles_d_issues_github_valides():
    """Un YAML invalide fait disparaître le formulaire sur GitHub (dont celui du droit de réponse)."""
    import yaml

    for f in sorted((site.RACINE / ".github" / "ISSUE_TEMPLATE").glob("*.yml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        assert isinstance(d, dict), f
        if f.name != "config.yml":
            assert d.get("name") and d.get("description") and d.get("body"), f
