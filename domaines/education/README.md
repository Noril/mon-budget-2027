# Éducation

Scolarité obligatoire (origine sociale des collégiens, acquis en sixième, brevet) et niveau d'études des jeunes adultes comparé à l'Union européenne.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `education.ips_colleges` | depp-ips-colleges + depp-effectifs-colleges + COG | France, département | rentrée 2025-2026 |
| `education.ips_colleges_dispersion` | depp-ips-colleges + COG | France, département | rentrée 2025-2026 |
| `education.eleves_colleges_defavorises` | depp-ips-colleges + depp-effectifs-colleges + COG | France, département | rentrée 2025-2026 |
| `education.reussite_dnb` | depp-dnb-departements + COG | France, département | session 2025 |
| `education.ecart_dnb_ips` | depp-va-colleges + depp-ips-colleges + COG | France | session 2025 |
| `education.eval6e_maths` | depp-evaluations-6e-departements + COG | France, département | 2025 |
| `education.eval6e_francais` | depp-evaluations-6e-departements + COG | France, département | 2025 |
| `education.sorties_precoces` | eurostat-edat-lfse-14 | France, pays (UE) | 2025 |
| `education.diplomes_superieur_25_34` | eurostat-edat-lfse-03 | France, pays (UE) | 2025 |

## Premiers constats

- En 2025, 32,5 % des élèves entrant en sixième se situent dans les deux groupes de maîtrise les plus faibles en mathématiques (30,8 % en 2017), avec un écart de 21,0 % à Paris à 89,7 % à Mayotte.
- À la session 2025 du brevet, la réussite en série générale est supérieure de 16,6 points dans le quart des collèges les plus favorisés socialement à celle du quart le plus défavorisé.
- L'IPS moyen des collégiens va de 70,2 à Mayotte à 129,5 à Paris à la rentrée 2025, et la ségrégation entre collèges est la plus forte dans les Hauts-de-Seine (écart-type de 22,6 points contre 5,1 dans la Creuse).
- La France compte 7,2 % de sorties précoces chez les 18-24 ans en 2025, sous la moyenne de l'UE (9,1 %) et l'objectif européen de 9 %.
- En 2025, 55,8 % des 25-34 ans sont diplômés du supérieur en France contre 44,8 % dans l'UE.

Valeurs lues dans `data/indicateurs/` (versions 1.0.0) ; à appeler par `{{ind:…}}` dans toute fiche future.
