from __future__ import annotations

from verifications._securite_commun import calculer_taux


def calculer() -> list[dict]:
    return calculer_taux({"Vols avec armes", "Vols violents sans arme"}, "insee_pop")


if __name__ == "__main__":
    for r in calculer()[:10]:
        print(r)
