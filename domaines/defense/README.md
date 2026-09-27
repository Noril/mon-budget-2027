# Défense

Effort de défense (en comptabilité nationale et au sens de l'OTAN), structure des dépenses et effectifs des armées, en France et comparés aux pays de l'UE et de l'OTAN. Aucune fiche de constat ni de proposition pour l'instant.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `defense.depenses_defense_pib` | eurostat-gov-10a-exp-defense (COFOG GF02) | France, pays (UE27) | 2024 (provisoire) |
| `defense.depenses_defense_part` | eurostat-gov-10a-exp-defense | France, pays (UE27) | 2024 (provisoire) |
| `defense.part_investissement_defense` | eurostat-gov-10a-exp-defense | France, pays (UE27) | 2024 (provisoire) |
| `defense.depenses_otan_pib` | otan-depenses-defense (tableau 3) | France, pays (Alliés, agrégats OTAN) | 2026 (estimation OTAN) |
| `defense.part_equipement_otan` | otan-depenses-defense (tableau 8a) | France, pays (Alliés) | 2026 (estimation OTAN) |
| `defense.personnel_militaire_otan` | otan-depenses-defense (tableau 7) | France, pays (Alliés, agrégats OTAN) | 2026 (estimation OTAN) |
| `defense.effectifs_militaires` | armees-militaires-carriere-contrat | France | 2024 |

Trous : aucune donnée ouverte par pays ne mesure la part des équipements achetés à des fournisseurs européens (l'Agence européenne de défense ne publie que des agrégats en PDF) ; la base Milex du SIPRI n'est pas sous licence ouverte et n'est pas branchée ; les réservistes et les civils de la défense ne sont pas encore suivis (jeux disponibles sur data.gouv.fr).

## Premiers constats

Valeurs lues dans les tables calculées (`data/indicateurs/`) le 27 septembre 2026 ; les fiches devront les appeler par `{{ind:…}}`.

- En comptabilité nationale, la France consacre 1,9 % de son PIB à la défense en 2024 (provisoire), contre 1,5 % en moyenne dans l'UE, 1,4 % en Allemagne et 2,9 % en Pologne : 8e rang des Vingt-Sept. La moyenne européenne est passée de 1,1 % en 2014 à 1,5 % ; la France, de 1,8 % en 2017 à 1,9 %.
- Au sens de l'OTAN (dépenses « core », pensions comprises), la France passe de 1,82 % du PIB en 2014 à 2,04 % en 2024 et 2,22 % estimés en 2026, mais recule dans le classement des Alliés : 6e sur 31 en 2014, 15e en 2024, 16e en 2026, loin de la Pologne (4,68 %) et des pays baltes, et derrière l'Allemagne (2,69 %) et le Royaume-Uni (2,56 %).
- La part de l'équipement dans les dépenses de défense (définition OTAN) monte de 24,6 % en 2014 à 27,5 % en 2024 et 34,1 % estimés en 2026, au-dessus du repère de 20 % ; en comptabilité nationale, la formation brute de capital fixe représente 18,4 % des dépenses de défense en 2024, contre 21,6 % en moyenne dans l'UE (17e rang des Vingt-Sept).
- Les effectifs militaires du ministère des Armées (hors gendarmerie) sont passés de 246 800 ETPT en 2002 à 200 500 en 2015, puis 197 000 en 2024 : la remontée prévue par les lois de programmation militaire ne se lit pas encore, l'effectif reculant même depuis 2021 (203 800).
- La défense pèse 3,2 % des dépenses publiques françaises en 2024, contre 3,0 % en moyenne dans l'UE : l'écart est moindre qu'en points de PIB, la dépense publique totale étant plus élevée en France.
