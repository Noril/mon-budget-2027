from __future__ import annotations

from verifications._agents_fp_1000hab import calculer as _calculer


def calculer() -> list[dict]:
    return _calculer("EFFECTIFS_FP_HOSPITALIERE", "FPH")
