from __future__ import annotations

from verifications._dgef_commun import calculer_titres_motif


def calculer() -> list[dict]:
    return calculer_titres_motif("TOTAL")


if __name__ == "__main__":
    for r in calculer():
        print(r)
