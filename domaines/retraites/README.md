# Retraites

Montant des pensions, âge de départ, niveau de vie relatif des retraités et poids des dépenses de vieillesse.
Sources au catalogue : `catalogue/retraites.yaml` ; définitions dans `indicateurs/retraites/`.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `retraites.pension_moyenne_rg` | cnav-pension-moyenne | France (régime général) | 2025 |
| `retraites.age_moyen_depart` | cnav-age-attribution | France (régime général) | 2025 |
| `retraites.taux_remplacement_agrege` | eurostat-ilc-pnp3 | France, pays | 2025 (revenus 2024) |
| `retraites.revenu_relatif_65` | eurostat-ilc-pnp2 | France, pays | 2025 (revenus 2024) |
| `retraites.depense_vieillesse_survie` | eurostat-spr-exp-func | France, pays | 2024 (UE : 2023) |

Les deux séries CNAV ne couvrent que le régime général (retraite de base, hors complémentaires) : elles ne disent rien
des fonctionnaires ni des régimes spéciaux, et la pension moyenne est très inférieure à la pension tous régimes.

## Premiers constats

Valeurs lues dans `data/indicateurs/` (calcul du 27 septembre 2026) ; à appeler par `{{ind:…}}` dans les fiches.

- L'âge moyen d'attribution d'une retraite de droit direct au régime général atteint 63,7 ans en 2025, contre 63,4 ans en 2023 (`retraites.age_moyen_depart`).
- La retraite de base moyenne de droit direct servie par le régime général est de 916 € bruts par mois fin 2025, contre 838 € fin 2023 (`retraites.pension_moyenne_rg`).
- Le niveau de vie médian des 65 ans ou plus atteint 97 % de celui des moins de 65 ans en France en 2025, contre 91 % dans l'UE à 27 (`retraites.revenu_relatif_65`).
- Le taux de remplacement agrégé de la France (61 % en 2025) est proche de la moyenne de l'UE à 27 (60 %), loin derrière l'Italie (80 %) et l'Espagne (81 %) (`retraites.taux_remplacement_agrege`).
- Les prestations vieillesse et survie représentent 14,6 % du PIB en France en 2024, quatrième niveau de l'UE, contre 12,5 % pour l'UE à 27 en 2023 (`retraites.depense_vieillesse_survie`).

## À brancher

- Pension moyenne tous régimes (droit direct, base et complémentaire) et âge conjoncturel de départ : DREES, « Les
  retraités et les retraites », diffusé en classeurs XLSX (normalisation dédiée à écrire).
- Âge et pension par département : non publiés en open data par la CNAV à ce jour.
