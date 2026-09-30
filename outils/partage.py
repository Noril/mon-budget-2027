"""Images d'aperçu (Open Graph, 1200 × 630) pour le partage des pages sur les réseaux sociaux.

Dessinées avec Pillow dans l'identité du site (fond gris clair, bulletins blancs, encre bleu nuit, violet du tampon),
avec les polices embarquées d'outils/polices/ converties du woff2 à la volée.
"""

from __future__ import annotations

import io
from functools import cache

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .theme import POLICES

L, H = 1200, 630
FOND, BULLETIN, ENCRE, GRIS, LIGNE, TAMPON = "#eef0f3", "#ffffff", "#1c2230", "#505a69", "#d3d8df", "#5a3e9b"


@cache
def _ttf(fichier: str) -> bytes:
    f = TTFont(str(POLICES / fichier))
    f.flavor = None
    tampon = io.BytesIO()
    f.save(tampon)
    return tampon.getvalue()


def police(nom: str, taille: int) -> ImageFont.FreeTypeFont:
    fichier = {"titre": "big-shoulders-display-latin-800-normal.woff2", "texte": "Luciole-Regular.woff2",
               "gras": "Luciole-Bold.woff2"}[nom]
    return ImageFont.truetype(io.BytesIO(_ttf(fichier)), taille)


def _lignes(d: ImageDraw.ImageDraw, texte: str, f: ImageFont.FreeTypeFont, largeur: int) -> list[str]:
    mots, lignes, cour = texte.split(), [], ""
    for m in mots:
        essai = f"{cour} {m}".strip()
        if d.textlength(essai, font=f) <= largeur:
            cour = essai
        else:
            lignes.append(cour)
            cour = m
    return lignes + ([cour] if cour else [])


def _cadre(titre: str, pied: str = "mon-budget-2027.fr") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(im)
    d.text((64, 48), "Mon budget 2027", font=police("titre", 44), fill=ENCRE)
    d.rectangle((64, 106, L - 64, 109), fill="#aab3be")
    y = 136
    for ligne in _lignes(d, titre, police("titre", 84), L - 128)[:2]:
        d.text((64, y), ligne, font=police("titre", 84), fill=ENCRE)
        y += 84
    d.text((64, H - 64), pied, font=police("gras", 26), fill=TAMPON)
    return im, d


def _bulletin(d: ImageDraw.ImageDraw, x: int, y: int, l: int, h: int, nom: str, montant: str, legende: str) -> None:
    d.rectangle((x + 4, y + 6, x + l + 4, y + h + 6), fill="#d5dae1")
    d.rectangle((x, y, x + l, y + h), fill=BULLETIN, outline=LIGNE, width=2)
    fn = police("gras", 22)
    d.text((x + l / 2, y + 22), nom, font=fn, fill=ENCRE, anchor="mt")
    d.line((x + 18, y + 60, x + l - 18, y + 60), fill=LIGNE, width=2)
    d.text((x + l / 2, y + h - 16), montant, font=police("titre", 62), fill=ENCRE, anchor="ms")
    if legende:
        d.text((x + l / 2, y + h - 8), legende, font=police("texte", 15), fill=GRIS, anchor="ms")


def accueil(programmes: list[tuple[str, str]]) -> Image.Image:
    """programmes : (nom court, montant affiché), dans l'ordre alphabétique."""
    im, d = _cadre("Ce que coûteraient les promesses")
    l, h, gx, gy = 252, 140, 21, 18
    for i, (nom, montant) in enumerate(programmes[:8]):
        _bulletin(d, 64 + (i % 4) * (l + gx), 238 + (i // 4) * (h + gy), l, h, nom, montant, "")
    d.text((L - 64, H - 64), "Md€ de déficit en plus chaque année (2032)", font=police("texte", 24), fill=GRIS, anchor="ra")
    return im


def programme(nom: str, parti: str, montant: str, legende: str) -> Image.Image:
    im, d = _cadre(nom)
    d.text((64, 230), parti, font=police("texte", 30), fill=GRIS)
    x, y, l, h = 64, 300, 640, 220
    d.rectangle((x + 5, y + 7, x + l + 5, y + h + 7), fill="#d5dae1")
    d.rectangle((x, y, x + l, y + h), fill=BULLETIN, outline=LIGNE, width=2)
    d.text((x + 36, y + 142), montant, font=police("titre", 130), fill=ENCRE, anchor="ls")
    for k, ligne in enumerate(_lignes(d, legende, police("texte", 26), l - 72)[:2]):
        d.text((x + 36, y + 176 + k * 32), ligne, font=police("texte", 26), fill=GRIS, anchor="ls")
    d.text((770, 330), "Chaque mesure citée", font=police("gras", 28), fill=ENCRE)
    d.text((770, 368), "et chiffrée, sources", font=police("gras", 28), fill=ENCRE)
    d.text((770, 406), "à l'appui.", font=police("gras", 28), fill=ENCRE)
    return im


def generique(titre: str, texte: str, pile: bool = False) -> Image.Image:
    im, d = _cadre(titre)
    y = 330
    for ligne in _lignes(d, texte, police("texte", 34), 700)[:4]:
        d.text((64, y), ligne, font=police("texte", 34), fill=GRIS)
        y += 46
    if pile:  # pile de bulletins, comme sur l'écran d'accueil du jeu
        for angle, dx, dy, bord in ((-8, 0, 0, False), (5, 6, -4, False), (-1, 3, -2, True)):
            carte = Image.new("RGBA", (300, 220), (0, 0, 0, 0))
            c = ImageDraw.Draw(carte)
            c.rectangle((10, 10, 290, 210), fill=BULLETIN, outline=LIGNE, width=2)
            if bord:
                c.rectangle((10, 10, 290, 26), fill=TAMPON)
            carte = carte.rotate(angle, expand=True, resample=Image.BICUBIC)
            im.paste(carte, (840 + dx, 300 + dy), carte)
    return im


def png(im: Image.Image) -> bytes:
    tampon = io.BytesIO()
    im.save(tampon, "PNG", optimize=True)
    return tampon.getvalue()
