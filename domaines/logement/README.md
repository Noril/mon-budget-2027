# Logement

Construction neuve, prix des logements et état du parc social. Diagnostic et propositions : à instruire.

## Indicateurs

| Indicateur | Source | Maille | Dernière période |
| --- | --- | --- | --- |
| `logement.logements_autorises` | sdes-sitadel-departements + insee-estimations-population | France (hors Mayotte), département | 2025 |
| `logement.logements_commences` | sdes-sitadel-departements + insee-estimations-population | France (hors Mayotte), département | 2025 |
| `logement.prix_m2_logements` | dgfip-dvf-statistiques | France (hors Alsace-Moselle et Mayotte), département | 2025 |
| `logement.parc_social_dpe_fg` | sdes-rpls-logements | France métropolitaine, département | 2025 (parc au 1er janvier) |

Pas de comparaison européenne pour l'instant : Eurostat ne publie ni permis ni mises en chantier harmonisés par habitant ; l'indice des prix des logements (`prc_hpi_a`) est un indice, pas un niveau.

## Premiers constats

- Les mises en chantier restent à 3,84 logements pour 1 000 habitants en 2025 après 3,80 en 2024, les deux plus bas niveaux depuis 2000 et moitié moins qu'en 2006 (7,82).
- Les autorisations ont un peu remonté en 2025 (5,41 pour 1 000 habitants après 4,70 en 2024) sans rattraper 2022 (7,17), et l'écart entre départements va de 0,73 à Paris à 11,56 en Haute-Savoie.
- Le prix moyen des ventes de maisons et d'appartements s'établit à 3 228 €/m² en 2025, en léger rebond après le repli de 2023-2024 (3 340 €/m² en 2022), avec un rapport de un à dix entre la Creuse (930 €/m²) et Paris (10 059 €/m²).
- Au 1er janvier 2025, 3,1 % des logements sociaux de métropole dont l'étiquette est connue sont classés F ou G, mais la part atteint 24,7 % dans les Hautes-Alpes et 11,4 % en Corrèze.

## Non branché

- Vacance et loyers du parc social : absents du fichier RPLS détaillé, publiés seulement en tableaux agrégés par le SDES.
- Médiane annuelle des prix : nécessite le fichier géolocalisé geo-dvf (plusieurs centaines de Mo par an).
