# Solidarités

Pauvreté, inégalités de revenus, minima sociaux et poids de la protection sociale. Sources au catalogue :
`catalogue/solidarites.yaml` ; définitions dans `indicateurs/solidarites/`.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `solidarites.taux_pauvrete_filosofi` | insee-filosofi + COG | France métropolitaine, région, département | 2023 |
| `solidarites.niveau_vie_median` | insee-filosofi + COG | France métropolitaine, région, département | 2023 |
| `solidarites.taux_pauvrete_erfs` | insee-erfs-retropole | France métropolitaine | 2024 |
| `solidarites.taux_risque_pauvrete` | eurostat-ilc-li02 | France, pays | 2025 (revenus 2024) |
| `solidarites.rapport_s80_s20` | eurostat-ilc-di11 | France, pays | 2025 (revenus 2024) |
| `solidarites.depense_protection_sociale` | eurostat-spr-exp-type | France, pays | 2024 (UE : 2023) |
| `solidarites.part_pop_rsa` | caf-allocataires-departement + populations de référence + COG | France hors Mayotte, département | 2025 (décembre) |
| `solidarites.part_pop_prime_activite` | caf-allocataires-departement + populations de référence + COG | France hors Mayotte, département | 2025 (décembre) |

Trois mesures du taux de pauvreté coexistent et ne se comparent pas entre elles : Filosofi (exhaustif fiscal, seul
à descendre au département), ERFS (mesure officielle nationale) et EU-SILC (comparaison européenne).

## Premiers constats

Valeurs lues dans `data/indicateurs/` (calcul du 27 septembre 2026) ; à appeler par `{{ind:…}}` dans les fiches.

- En 2023, le taux de pauvreté va de 9,2 % en Vendée à 29,5 % en Seine-Saint-Denis et 36,4 % à La Réunion, pour 15,9 % en France métropolitaine (`solidarites.taux_pauvrete_filosofi`).
- Le taux de pauvreté officiel est remonté de 14,4 % en 2022 à 15,4 % en 2023 et s'y maintient en 2024 (`solidarites.taux_pauvrete_erfs`).
- Mesuré à l'européenne, le taux de risque de pauvreté de la France (16,3 % en 2025) a rejoint la moyenne de l'UE à 27 (16,3 %), alors qu'il en était inférieur de 0,8 point en 2023 (`solidarites.taux_risque_pauvrete`).
- La France consacre 34,4 % de son PIB à la protection sociale en 2024, le niveau le plus élevé de l'UE, contre 27,8 % pour l'UE à 27 en 2023 (`solidarites.depense_protection_sociale`).
- Fin 2025, le RSA couvre 5,4 % de la population (hors Mayotte), de 1,8 % en Vendée à 26,9 % en Guyane, et la prime d'activité 13,0 % (`solidarites.part_pop_rsa`, `solidarites.part_pop_prime_activite`).

## À brancher

- Allocataires du RSA relevant de la MSA (hors champ CAF) : série DREES « minima sociaux » par département, à rapprocher.
- Filosofi aux mailles EPCI et commune (présentes dans la source, avec secret statistique) si une fiche en a besoin.
