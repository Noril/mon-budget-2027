"""Connecteurs avec réponses HTTP simulées : aucun accès réseau."""

import contextlib
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from pipelines.connecteurs import api_rest, connecteur, dido, fichier, fichiers_nommes, opendatasoft, sdmx


class Reponse:
    def __init__(self, contenu=b"", entetes=None, url="https://exemple.test/x", json_=None, statut=200):
        self.contenu, self.headers, self.url, self._json, self.statut = contenu, entetes or {}, httpx.URL(url), json_, statut

    def raise_for_status(self):
        if self.statut >= 400:
            raise httpx.HTTPStatusError("erreur", request=None, response=None)

    def iter_bytes(self, taille):
        yield self.contenu

    def json(self):
        return self._json


@pytest.fixture
def reseau(monkeypatch):
    """Sert des réponses préparées dans l'ordre ; garde la trace des requêtes."""
    file, appels = [], []

    def prochaine(methode, url, **kw):
        appels.append((methode, str(url), kw))
        r = file.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    @contextlib.contextmanager
    def stream(methode, url, **kw):
        yield prochaine(methode, url, **kw)

    monkeypatch.setattr(httpx, "stream", stream)
    monkeypatch.setattr(httpx, "get", lambda url, **kw: prochaine("GET", url, **kw))
    monkeypatch.setattr(httpx, "head", lambda url, **kw: prochaine("HEAD", url, **kw))
    return file, appels


def test_resolution_du_connecteur_par_mode():
    assert connecteur("api-rest") is api_rest
    assert connecteur("fichiers-nommes") is fichiers_nommes
    assert connecteur("n-existe-pas") is None


def test_sdmx_url_et_telechargement(reseau, tmp_path):
    file, appels = reseau
    source = {"id": "e", "titre": "T", "licence": "L", "acces": {"url": "https://api.test/data/ds/", "cle": "A.B", "parametres": {"format": "SDMX-CSV"}}}
    assert sdmx.url_requete(source) == "https://api.test/data/ds/A.B"
    file.append(Reponse(b"a,b\n1,2\n", {"content-type": "text/csv; charset=utf-8"}, "https://api.test/data/ds/A.B"))
    [(url, chemin)] = sdmx.telecharger(source, tmp_path / "brut")
    assert chemin.read_bytes() == b"a,b\n1,2\n" and url.endswith("A.B")
    assert appels[0][2]["params"] == {"format": "SDMX-CSV"}
    assert sdmx.metadonnees(source)["modifie_le"] is None


def test_sdmx_refuse_un_contenu_non_csv(reseau, tmp_path):
    reseau[0].append(Reponse(b"<html>", {"content-type": "text/html"}))
    with pytest.raises(ValueError, match="CSV attendu"):
        sdmx.telecharger({"id": "e", "acces": {"url": "https://api.test/d"}}, tmp_path)


def test_sdmx_erreur_http_propagee(reseau, tmp_path):
    reseau[0].append(Reponse(statut=503))
    with pytest.raises(httpx.HTTPStatusError):
        sdmx.telecharger({"id": "e", "acces": {"url": "https://api.test/d"}}, tmp_path)


@pytest.mark.parametrize("type_contenu,extension", [
    ("application/vnd.apache.parquet; parquet", ".parquet"), ("text/csv", ".csv"), ("application/json", ".json"),
    ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
])
def test_api_rest_deduit_l_extension(reseau, tmp_path, type_contenu, extension):
    reseau[0].append(Reponse(b"x", {"content-type": type_contenu}))
    [(_, chemin)] = api_rest.telecharger({"id": "r", "acces": {"url": "https://api.test/e"}}, tmp_path)
    assert chemin.name == f"donnees{extension}" and not (tmp_path / "donnees.tmp").exists()


def test_api_rest_type_inconnu(reseau, tmp_path):
    reseau[0].append(Reponse(b"x", {"content-type": "application/zip"}))
    with pytest.raises(ValueError, match="non reconnu"):
        api_rest.telecharger({"id": "r", "acces": {"url": "https://api.test/e"}}, tmp_path)


def test_fichier_telecharger_reessaie_sur_coupure(reseau, tmp_path):
    file, appels = reseau
    file += [httpx.ReadError("coupure"), Reponse(b"ok")]
    chemin = fichier.telecharger_url("https://x.test/a.csv", tmp_path / "a.csv")
    assert chemin.read_bytes() == b"ok" and len(appels) == 2


def test_fichier_abandonne_apres_les_essais(reseau, tmp_path):
    reseau[0].extend([httpx.ReadError("coupure")] * 3)
    with pytest.raises(httpx.ReadError):
        fichier.telecharger_url("https://x.test/a.csv", tmp_path / "a.csv")


def test_fichier_ne_reessaie_pas_sur_404(reseau, tmp_path):
    file, appels = reseau
    file.append(Reponse(statut=404))
    with pytest.raises(httpx.HTTPStatusError):
        fichier.telecharger_url("https://x.test/a.csv", tmp_path / "a.csv")
    assert len(appels) == 1


def test_fichier_date_melodi_en_heure_de_paris(reseau):
    file, _ = reseau
    file.append(Reponse(json_={"product": [{"id": "autre", "modified": "2020-01-01T00:00:00"},
                                           {"id": "P1", "modified": "2025-07-01T10:00:00.123"}]}))
    assert fichier._modifie_melodi("https://api.insee.fr/melodi/file/DS_X/P1") == "2025-07-01T10:00:00+02:00"
    assert fichier._modifie_melodi("https://autre.test/f.csv") is None


def test_opendatasoft_prend_la_date_la_plus_recente(reseau):
    reseau[0].append(Reponse(json_={"metas": {"default": {
        "title": "Jeu", "license": "ODbL", "modified": "2024-01-01T00:00:00+00:00", "data_processed": "2025-03-01T00:00:00+00:00"}}}))
    m = opendatasoft.metadonnees({"acces": {"portail": "https://p.test/", "jeu": "j"}})
    assert m["modifie_le"] == "2025-03-01T00:00:00+00:00" and m["titre"] == "Jeu"


def test_opendatasoft_pieces_et_export(reseau, tmp_path):
    file, appels = reseau
    src = {"acces": {"portail": "https://p.test", "jeu": "j", "pieces": ["tableau_xlsx"]}}
    file.append(Reponse(b"x"))
    [(url, chemin)] = opendatasoft.telecharger(src, tmp_path)
    assert url == "https://p.test/api/explore/v2.1/catalog/datasets/j/attachments/tableau_xlsx" and chemin.name == "tableau.xlsx"
    file.append(Reponse(b"p"))
    [(url, chemin)] = opendatasoft.telecharger({"acces": {"portail": "https://p.test", "jeu": "j"}}, tmp_path / "b")
    assert url.endswith("/datasets/j/exports/parquet") and chemin.name == "donnees.parquet"


def test_fichiers_nommes_noms_surs():
    assert fichiers_nommes.nom_fichier("https://x.test/a/b.zip", None) == "b.zip"
    nom = fichiers_nommes.nom_fichier("https://x.test/dl", 'attachment; filename="../a b.csv"')
    assert "/" not in nom and " " not in nom and nom.endswith(".csv")
    assert fichiers_nommes.nom_fichier("https://x.test/", None) == "donnees"
    assert fichiers_nommes.nom_fichier("https://x.test/d", "attachment; filename*=UTF-8''rapport%202024.xlsx") == "rapport_2024.xlsx"


def test_fichiers_nommes_rang_evite_les_collisions(reseau, tmp_path):
    file, _ = reseau
    file += [Reponse(b"1"), Reponse(b"2")]
    src = {"acces": {"urls": ["https://x.test/16/D.zip", "https://x.test/17/D.zip"]}}
    res = fichiers_nommes.telecharger(src, tmp_path)
    assert [c.name for _, c in res] == ["01_D.zip", "02_D.zip"]
    assert [c.read_bytes() for _, c in res] == [b"1", b"2"]


def test_dido_retient_le_dernier_millesime_deja_diffuse(reseau):
    futur = (datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    file, _ = reseau
    file += [Reponse(json_={"dataset": {"id": "ds"}}),
             Reponse(json_={"datafiles": [{"rid": "autre", "millesimes": []}, {"rid": "R", "millesimes": [
                 {"millesime": "2023-01", "date_diffusion": "2023-02-01T00:00:00Z", "rows": 5},
                 {"millesime": "2024-01", "date_diffusion": "2024-02-01T00:00:00Z", "rows": 6},
                 {"millesime": "2025-01", "date_diffusion": futur, "rows": 7}]}]})]
    m = dido.metadonnees({"titre": "T", "licence": "L", "id": "d", "acces": {"url": "https://dido.test/api/v1/datafiles/R"}})
    assert m["millesime"] == "2024-01" and m["modifie_le"].startswith("2024-02-01")


def test_dido_sans_millesime_diffuse(reseau):
    futur = (datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    reseau[0].extend([Reponse(json_={"dataset": {"id": "ds"}}),
                      Reponse(json_={"datafiles": [{"rid": "R", "millesimes": [{"millesime": "2030", "date_diffusion": futur}]}]})])
    with pytest.raises(ValueError, match="aucun millésime diffusé"):
        dido._millesime({"id": "d", "acces": {"url": "https://dido.test/api/v1/datafiles/R"}})
