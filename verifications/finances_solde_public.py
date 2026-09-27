"""Recalcul indépendant de finances.solde_public.

France : INSEE DD_CNA_APU (insee-comptes-apu), REF_SECTOR=S13, STO=B9, CONSOLIDATION=C,
ACCOUNTING_ENTRY=B, EXPENDITURE=_Z, UNIT_MEASURE=XDC, rapporté au PIB INSEE DD_CNA_AGREGATS
(insee-pib, STO=B1GQ, PRICES=V, UNIT_MEASURE=XDC, TRANSFORMATION=N, COUNTERPART_AREA=W0) de la
même année, x100, sans arrondi. Lignes identiques dédoublonnées.

Pays (maille "pays", y compris le code FR) : Eurostat gov_10dd_edpt1, unit=MIO_NAC, sector=S13,
na_item B9 / na_item B1GQ (sector S1) x100, par pays et année ; agrégats EU27_2020 et zones euro
compris.

Ces deux séries occupent des mailles différentes (france vs pays) et peuvent différer pour le
code FR (millésimes différents), sans conflit de clé.
"""

from __future__ import annotations

import duckdb

from pipelines.commun import NORMALISE


def _lignes_brutes(fichier) -> list[dict]:
    con = duckdb.connect()
    curseur = con.execute(f"select * from read_parquet('{fichier.as_posix()}')")
    colonnes = [d[0] for d in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]


def _code_libelle(geo: str) -> tuple[str, str]:
    code, _, libelle = geo.partition(":")
    return code, libelle


def _calculer_france() -> list[dict]:
    apu = _lignes_brutes(NORMALISE / "insee-comptes-apu.parquet")
    pib_brut = _lignes_brutes(NORMALISE / "insee-pib.parquet")

    b9: dict[str, float] = {}
    vues: set[tuple] = set()
    for ligne in apu:
        if ligne["REF_SECTOR"] != "S13":
            continue
        if ligne["STO"] != "B9":
            continue
        if ligne["CONSOLIDATION"] != "C":
            continue
        if ligne["ACCOUNTING_ENTRY"] != "B":
            continue
        if ligne["EXPENDITURE"] != "_Z":
            continue
        if ligne["UNIT_MEASURE"] != "XDC":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])
        cle = (annee, valeur)
        if cle in vues:
            continue
        vues.add(cle)
        b9[annee] = valeur

    pib: dict[str, float] = {}
    for ligne in pib_brut:
        if ligne["STO"] != "B1GQ":
            continue
        if ligne["PRICES"] != "V":
            continue
        if ligne["UNIT_MEASURE"] != "XDC":
            continue
        if ligne["TRANSFORMATION"] != "N":
            continue
        if ligne["COUNTERPART_AREA"] != "W0":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        pib[ligne["TIME_PERIOD"]] = float(ligne["OBS_VALUE"])

    resultat = []
    for annee, num in b9.items():
        if annee not in pib:
            continue
        valeur = 100.0 * num / pib[annee]
        resultat.append({"maille": "france", "code": "FR", "libelle": "France", "periode": annee, "valeur": valeur})
    return resultat


def _calculer_pays() -> list[dict]:
    gov = _lignes_brutes(NORMALISE / "eurostat-gov-10dd-edpt1.parquet")

    b9: dict[tuple[str, str], float] = {}
    b1gq: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}

    for ligne in gov:
        if ligne["unit"] != "MIO_NAC:Millions d'unités de monnaie nationale":
            continue
        if ligne["OBS_VALUE"] is None:
            continue
        code, libelle = _code_libelle(ligne["geo"])
        annee = ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])
        libelles[code] = libelle

        if ligne["sector"] == "S13:Administrations publiques" and ligne["na_item"] == "B9:Capacité de financement (+)/besoin de financement (-)":
            b9[(code, annee)] = valeur
        elif ligne["sector"] == "S1:Economie totale" and ligne["na_item"] == "B1GQ:Produit intérieur brut aux prix du marché":
            b1gq[(code, annee)] = valeur

    resultat = []
    for (code, annee), num in b9.items():
        if (code, annee) not in b1gq:
            continue
        valeur = 100.0 * num / b1gq[(code, annee)]
        resultat.append({"maille": "pays", "code": code, "libelle": libelles[code], "periode": annee, "valeur": valeur})
    return resultat


def calculer() -> list[dict]:
    return _calculer_france() + _calculer_pays()


if __name__ == "__main__":
    for r in sorted(calculer(), key=lambda x: (x["maille"], x["code"], x["periode"]))[:10]:
        print(r)
