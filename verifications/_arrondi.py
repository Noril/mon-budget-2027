"""Convention d'arrondi du dépôt, identique à ROUND de DuckDB : x × 10^n en virgule flottante, arrondi à l'entier
le plus proche avec les demis loin de zéro (std::round), puis ÷ 10^n.

Le round() de Python arrondit les demis au pair (6,25 -> 6,2) : ne pas l'utiliser dans les vérifications.
"""

import math


def arrondi(x: float, decimales: int = 0) -> float:
    if not math.isfinite(x):
        return x  # NaN et infinis passent tels quels, comme dans DuckDB
    puissance = 10.0 ** decimales
    m = x * puissance
    entier = math.floor(abs(m))
    if abs(m) - entier >= 0.5:
        entier += 1
    return math.copysign(entier, m) / puissance
