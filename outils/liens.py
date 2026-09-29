"""Vérification en ligne des citations et des liens du chiffrage.

    uv run python -m outils.liens                  # citations des programmes + sources des barèmes
    uv run python -m outils.liens --catalogue      # ajoute les URL du catalogue de données

Pour chaque mesure, télécharge `citation.url`, en extrait le texte (HTML ou PDF) et vérifie que la citation y figure,
après normalisation (casse, espaces, apostrophes, guillemets, césures). Écrit build/liens.md et data/liens.json.
Les pages sont mises en cache dans data/cache_liens/ : relancer ne retélécharge pas.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import httpx

from pipelines.commun import DONNEES, RACINE, charger_catalogue, ecrire_json

from .chiffrage import lire_baremes, lire_programmes

CACHE = DONNEES / "cache_liens"
SORTIE = RACINE / "build" / "liens.md"
ENTETES = {"User-Agent": "Mozilla/5.0 (open-politics ; verification de citations)", "Accept-Language": "fr,en"}


def normaliser(texte: str) -> str:
    t = unicodedata.normalize("NFKC", html.unescape(texte)).lower()
    t = t.replace("­", "").replace("-\n", "")
    t = re.sub(r"[’‘ʼ`´]", "'", t)
    t = re.sub(r"[«»“”„\"•▪●■◦]", " ", t)
    t = re.sub(r"[‐‑‒–—−]", "-", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def texte_de(contenu: bytes, type_: str) -> str:
    if contenu[:5] == b"%PDF-" or "pdf" in type_:
        try:
            from pypdf import PdfReader

            return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(contenu)).pages)
        except Exception as e:  # PDF illisible ou scanné
            return f"__PDF_ILLISIBLE__ {e}"
    brut = contenu.decode("utf-8", errors="replace")
    brut = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", brut)
    return re.sub(r"(?s)<[^>]+>", " ", brut)


ARCHIVE = threading.Semaphore(2)  # web.archive.org refuse les connexions trop nombreuses


def _curl(url: str) -> tuple[int | None, bytes, str]:
    """Repli quand httpx échoue (TLS ancien, filtrage des robots) : curl gère mieux certains serveurs."""
    r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", ENTETES["User-Agent"], "-w", "\n%{http_code} %{content_type}",
                        url], capture_output=True)
    corps, _, fin = r.stdout.rpartition(b"\n")
    code, _, type_ = fin.decode(errors="replace").partition(" ")
    return (int(code) if code.isdigit() and int(code) else None), corps, type_


def telecharger(url: str) -> dict:
    """Renvoie {statut, texte|erreur}, avec cache disque."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cle = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".json")
    if cle.exists():
        return json.loads(cle.read_text(encoding="utf-8"))
    verrou = ARCHIVE if "web.archive.org" in url else contextlib.nullcontext()
    with verrou:
        try:
            r = httpx.get(url, headers=ENTETES, timeout=40, follow_redirects=True)
            code, corps, type_ = r.status_code, r.content, r.headers.get("content-type", "")
        except Exception as e:
            code, corps, type_, erreur = None, b"", "", f"{type(e).__name__} : {e}"[:200]
        if code is None or code in (403, 429) or code >= 500:
            for essai in range(3):
                c2, b2, t2 = _curl(url)
                if c2 and c2 < 400:
                    code, corps, type_ = c2, b2, t2
                    break
                code = c2 or code
                time.sleep(3 * (essai + 1))
    res = {"statut": code, "texte": texte_de(corps, type_) if code and code < 400 else ""}
    if not code:
        res["erreur"] = locals().get("erreur", "pas de réponse")
    cle.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return res


def citation_presente(citation: str, texte: str) -> tuple[bool, float]:
    """Vrai si la citation normalisée figure dans le texte ; sinon part des mots de la citation retrouvés dans l'ordre."""
    c, t = normaliser(citation), normaliser(texte)
    if not c:
        return True, 1.0
    # les points de suspension ou crochets marquent des coupes : chaque morceau doit figurer
    morceaux = [m.strip(" .") for m in re.split(r"\[…\]|\[\.\.\.\]|…|\.\.\.", c) if len(m.strip(" .")) > 3]
    if morceaux and all(m in t for m in morceaux):
        return True, 1.0
    # extraction PDF : césures et retours à la ligne insèrent des espaces au milieu des mots
    compact = re.sub(r"[\s-]", "", t)
    if morceaux and all(re.sub(r"[\s-]", "", m) in compact for m in morceaux):
        return True, 1.0
    mots = re.findall(r"\w+", c)
    pos, trouves = 0, 0
    for m in mots:
        i = t.find(m, pos)
        if i >= 0:
            trouves, pos = trouves + 1, i + len(m)
    return False, trouves / len(mots) if mots else 0.0


def verifier_citations() -> list[dict]:
    lignes = [(p["id"], m) for _, p in lire_programmes() for m in p["mesures"]]
    urls = sorted({m["citation"]["url"] for _, m in lignes})
    with ThreadPoolExecutor(12) as ex:
        pages = dict(zip(urls, ex.map(telecharger, urls)))
    res = []
    for prog, m in lignes:
        url, page = m["citation"]["url"], pages[m["citation"]["url"]]
        if re.search(r"youtube\.com|youtu\.be|dailymotion|tf1info\.fr/.*video|/video", url):
            etat, score = "vidéo", None
        elif page.get("statut") is None or page["statut"] >= 400:
            etat, score = "inaccessible", None
        elif page["texte"].startswith("__PDF_ILLISIBLE__"):
            etat, score = "pdf illisible", None
        else:
            ok, score = citation_presente(m["citation"]["texte"], page["texte"])
            # tous les mots dans l'ordre : la différence ne tient qu'à la mise en page (puces, appels de note, numéros de page)
            etat = "ok" if ok or score == 1.0 else ("approchée" if score >= 0.85 else "absente")
        res.append({"programme": prog, "mesure": m["id"], "url": url, "statut_http": page.get("statut"),
                    "etat": etat, "score": score, "erreur": page.get("erreur")})
    return res


def verifier_urls(urls: dict[str, str]) -> list[dict]:
    """urls : {url: origine}. Statut HTTP seulement."""
    def statut(u):
        p = telecharger(u)
        return {"url": u, "origine": urls[u], "statut_http": p.get("statut"), "erreur": p.get("erreur")}
    with ThreadPoolExecutor(12) as ex:
        return list(ex.map(statut, sorted(urls)))


def _pct(x: float | None) -> str:
    return "" if x is None else f"{round(100 * x)} %"


def rapport(citations: list[dict], autres: list[dict]) -> str:
    from collections import Counter

    l = ["# Vérification des liens et des citations", "",
         "Généré par `outils.liens`. « approchée » : au moins 85 % des mots de la citation retrouvés dans l'ordre "
         "(mise en forme, coupe ou extraction PDF à relire) ; « absente » : citation non retrouvée ; « inaccessible » : "
         "page refusée aux robots (403), introuvable ou hors ligne, à vérifier à la main ; « vidéo » : citation orale, à "
         "vérifier à l'écoute.", ""]
    c = Counter(r["etat"] for r in citations)
    l.append("Citations : " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + ".")
    ko = [r for r in autres if r["statut_http"] is None or r["statut_http"] >= 400]
    l += [f"Autres liens (barèmes, catalogue) : {len(autres)} testés, {len(ko)} en échec.", ""]
    for titre, filtre in (("Citations absentes", "absente"), ("Citations approchées", "approchée"),
                          ("Pages inaccessibles", "inaccessible"), ("PDF illisibles", "pdf illisible"),
                          ("Vidéos (vérification manuelle)", "vidéo")):
        rs = [r for r in citations if r["etat"] == filtre]
        if rs:
            l += [f"## {titre} ({len(rs)})", "", "| Programme | Mesure | Statut | Score | URL |", "| --- | --- | --- | --- | --- |"]
            l += [f"| {r['programme']} | {r['mesure']} | {r['statut_http'] or r['erreur']} | "
                  f"{_pct(r['score'])} | {r['url']} |" for r in rs]
            l.append("")
    if ko:
        l += [f"## Autres liens en échec ({len(ko)})", "", "| Origine | Statut | URL |", "| --- | --- | --- |"]
        l += [f"| {r['origine']} | {r['statut_http'] or r['erreur']} | {r['url']} |" for r in ko]
    return "\n".join(l) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--catalogue", action="store_true", help="teste aussi les URL du catalogue de données")
    args = parser.parse_args(argv)
    citations = verifier_citations()
    urls = {s["url"]: f"barème {b['id']}" for b in lire_baremes() for s in b["sources"] if s["url"].startswith("http")}
    if args.catalogue:
        for s in charger_catalogue().values():
            for u in [s["doc"], *s["acces"].get("urls", [])]:
                if u.startswith("http"):
                    urls.setdefault(u, f"catalogue {s['id']}")
    autres = verifier_urls(urls)
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(rapport(citations, autres), encoding="utf-8")
    ecrire_json(DONNEES / "liens.json", {"citations": citations, "liens": autres})
    print(SORTIE.read_text(encoding="utf-8").split("\n## ")[0])
    print(f"-> {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
