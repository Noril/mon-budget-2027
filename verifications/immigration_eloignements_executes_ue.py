from __future__ import annotations

from pipelines.commun import NORMALISE
from verifications._eurostat_ue_commun import calculer_taux_pour_population, lignes

FICHIER = NORMALISE / "eurostat-migr-eirtn.parquet"


def calculer() -> list[dict]:
    numerateur: dict[tuple[str, str], float] = {}
    libelles: dict[str, str] = {}
    for ligne in lignes(FICHIER):
        if not (ligne["citizen"].startswith("TOTAL") and ligne["c_dest"].startswith("TOTAL")
                and ligne["age"].startswith("TOTAL") and ligne["sex"].startswith("T") and ligne["unit"].startswith("PER")):
            continue
        code, _, libelle = ligne["geo"].partition(":")
        libelles[code] = libelle
        numerateur[(code, ligne["TIME_PERIOD"])] = float(ligne["OBS_VALUE"])

    return calculer_taux_pour_population(numerateur, libelles, 100_000)


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
