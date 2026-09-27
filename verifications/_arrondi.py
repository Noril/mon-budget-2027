"""Convention d'arrondi du dépôt : les demis s'éloignent de zéro (comme ROUND de DuckDB).

Le round() de Python arrondit les demis au pair (6,25 -> 6,2) : ne pas l'utiliser dans les vérifications.
"""

from decimal import ROUND_HALF_UP, Decimal


def arrondi(x: float, decimales: int = 0) -> float:
    pas = Decimal(1).scaleb(-decimales)
    return float(Decimal(repr(x)).quantize(pas, rounding=ROUND_HALF_UP))
