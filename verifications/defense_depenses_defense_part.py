from __future__ import annotations

from verifications._gov10a import lire_gov10a


def calculer() -> list[dict]:
    return lire_gov10a("eurostat-gov-10a-exp-defense", "PC_TOT", "GF02", "TE")
