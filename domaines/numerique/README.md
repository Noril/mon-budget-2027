# Numérique

Technologie et intelligence artificielle, chantier prioritaire du programme, sous l'angle d'un État efficace, modernisé, automatisé et numérisé. Sources au catalogue : `catalogue/numerique.yaml`.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `numerique.entreprises_ia` | eurostat-isoc-eb-ai | France, pays | 2025 |
| `numerique.grandes_entreprises_ia` | eurostat-isoc-eb-ai | France, pays | 2025 |
| `numerique.ia_generative_particuliers` | eurostat-isoc-ai-iaiu | France, pays | 2025 |
| `numerique.administration_en_ligne` | eurostat-isoc-ciegi-ac | France, pays | 2025 |
| `numerique.demarches_en_ligne` | dinum-observatoire-demarches | France | 2026-04 |
| `numerique.demarches_accessibles` | dinum-observatoire-demarches | France | 2026-04 |
| `numerique.specialistes_tic` | eurostat-isoc-sks-itspt | France, pays | 2025 |
| `numerique.solde_services_tic` | eurostat-bop-its6-det | France, pays | 2025 |
| `numerique.solde_services_tic_usa` | eurostat-bop-its6-det | France, pays | 2025 |
| `numerique.locaux_fibre` | arcep-thd-deploiements-communes + COG | France, région, département | 2026T2 |
| `numerique.emploi_informatique` | urssaf-effectifs-informatique + COG | France, région, département | 2025 |
| `numerique.emploi_informatique_evol5` | urssaf-effectifs-informatique + COG | France, région, département | 2025 |
| `numerique.top500_puissance` | top500-listes | France, pays | 2026-06 |

## Premiers constats

Valeurs lues dans les tables calculées le 27 septembre 2026, à rappeler par `{{ind:…}}` dans les fiches.

- En 2025, 18,2 % des entreprises françaises de 10 salariés ou plus utilisent l'IA (UE : 20,0 %), contre 58,0 % des entreprises de 250 salariés ou plus (UE : 55,0 %) : le retard français tient aux PME, pas aux grands groupes.
- Les Français sont en avance sur les usages individuels : 37,5 % des 16-74 ans ont utilisé une IA générative au cours des trois derniers mois de 2025 (UE : 32,7 %) et 68,5 % ont interagi en ligne avec une administration (UE : 57,7 %).
- En avril 2026, 89,4 % des démarches administratives essentielles suivies par la DINUM sont réalisables en ligne, mais seulement 10,0 % de celles-ci sont pleinement accessibles aux personnes handicapées.
- Le solde des échanges de services de télécommunications, d'informatique et d'information de la France est déficitaire depuis 2013 et atteint −5,4 Md€ en 2025, quand l'UE dégage un excédent de 236,4 Md€ avec le reste du monde, porté surtout par l'Irlande.
- La fibre est raccordable pour 95,3 % des locaux au deuxième trimestre 2026, mais pour 82,4 % dans le Cantal, 70,5 % en Martinique et 18,4 % à Mayotte ; dans le même temps, l'emploi salarié des activités informatiques (571 496 salariés fin 2025, dont 49,7 % en Île-de-France) recule depuis son pic de 589 809 fin 2023.

## À brancher

- Usage de l'IA par secteur d'activité (Eurostat `isoc_eb_ain2`) : le format d'indicateur n'a pas de dimension sectorielle.
- Couverture FttH comparable entre pays (étude européenne de couverture haut débit, indicateurs DESI), pour ajouter la maille pays à `numerique.locaux_fibre`.
- Emploi public du numérique de l'État (DINUM, rapport sur la filière numérique) et dépenses informatiques de l'État.
