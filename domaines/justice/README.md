# Justice

Pour commencer, l'administration pénitentiaire : population détenue, places et surpopulation (statistique mensuelle du ministère de la Justice), avec une comparaison européenne (Eurostat).

## Indicateurs

| Indicateur | Source | Maille | Dernière période |
| --- | --- | --- | --- |
| `justice.detenus` | justice-ecroues-mensuel | France | 2026-08 |
| `justice.places_operationnelles` | justice-ecroues-mensuel | France | 2026-08 |
| `justice.densite_carcerale` | justice-ecroues-mensuel | France | 2026-08 |
| `justice.occupation_prisons_ue` | eurostat-crim-pris-cap | France, pays (EU27_2020 calculé) | 2024 |
| `justice.taux_detention_ue` | eurostat-crim-pris-cap + eurostat-demo-gind | France, pays (EU27_2020 calculé) | 2024 |

Les classeurs mensuels n'ont ni API ni lien stable : chaque mois ajoute une URL au catalogue.

## Premiers constats

- Au 1er août 2026, 89 668 personnes sont détenues pour 63 303 places opérationnelles, soit une densité carcérale de 141,6 %.
- La densité carcérale a gagné près de 15 points en deux ans, de 126,9 % en juillet 2024 à 141,6 % en août 2026, car le nombre de détenus augmente bien plus vite que celui des places.
- Le nombre de détenus au 1er janvier est passé de 72 173 en 2023 à 86 140 en 2026.
- Selon Eurostat, les prisons françaises sont occupées à 129,3 % de leur capacité officielle en 2024, contre 96,5 % en moyenne dans l'UE, le troisième taux le plus élevé de l'UE après Chypre (227,6 %) et la Slovénie (134,2 %).
- Avec 117,5 détenus pour 100 000 habitants en 2024, la France incarcère un peu plus que la moyenne de l'UE (113,0) : la surpopulation vient donc surtout du manque de places.
