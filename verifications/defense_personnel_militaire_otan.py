from __future__ import annotations

from verifications._otan import lire_bloc


def calculer() -> list[dict]:
    return lire_bloc("Table 7", "Thousands")
