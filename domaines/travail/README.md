# Travail et emploi

Chômage, emploi et demandeurs d'emploi, en France, par territoire et comparés à l'Union européenne. Aucune fiche de constat ni de proposition pour l'instant.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `travail.taux_chomage` | insee-eec-series (France), eurostat-une-rt-a (pays) | France, pays (UE27) | 2025 |
| `travail.taux_chomage_localise` | insee-chomage-localise + COG | France, région, département | 2026-T2 |
| `travail.taux_emploi_20_64` | eurostat-lfsi-emp-a | France, pays (UE27) | 2025 |
| `travail.demandeurs_emploi_a` | dares-defm-stock-trim + COG | France, région, département | 2026-T2 |
| `travail.emploi_salarie_prive` | urssaf-effectifs-departements + COG | France, région, département | 2025 (31 décembre) |
| `travail.emploi_salarie_prive_evolution` | urssaf-effectifs-departements + COG | France, région, département | 2025 |

## Premiers constats

Valeurs lues dans les tables calculées (`data/indicateurs/`) le 27 septembre 2026 ; les fiches devront les appeler par `{{ind:…}}`.

- Le chômage remonte : 7,7 % de la population active en 2025 au sens du BIT (moyenne annuelle), contre 6,0 % dans l'UE, et le taux localisé atteint 8,3 % au deuxième trimestre 2026, contre 7,5 % un an plus tôt.
- Les écarts territoriaux restent très larges au deuxième trimestre 2026 : de 4,8 % dans le Cantal à 12,8 % dans les Pyrénées-Orientales en métropole, et jusqu'à 20,4 % en Guyane.
- Le taux d'emploi des 20-64 ans progresse (75,4 % en 2025 contre 70,2 % en 2015) mais reste sous la moyenne de l'UE (76,1 %) et loin de l'Allemagne (81,1 %).
- L'emploi salarié privé a reculé en 2025 (−0,27 % sur un an, 19,97 millions de salariés au 31 décembre), pour la première fois depuis 2020, et a baissé dans 76 départements sur 100.
- France Travail compte 3,32 millions d'inscrits en catégorie A au deuxième trimestre 2026 (CVS-CJO), contre 3,02 millions deux ans plus tôt, hausse gonflée par l'inscription automatique des allocataires du RSA et des jeunes suivis depuis 2025.
