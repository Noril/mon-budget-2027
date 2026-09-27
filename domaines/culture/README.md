# Culture

Dépense publique culturelle et emploi culturel (Eurostat, comparables dans l'UE), fréquentation des musées de France (ministère de la Culture).

## Indicateurs

| Indicateur | Source | Maille | Dernière période |
| --- | --- | --- | --- |
| `culture.depense_publique_culture` | eurostat-gov-10a-exp-culture + eurostat-nama-10-gdp-echanges | France, pays | 2024 |
| `culture.emploi_culturel` | eurostat-cult-emp-sex | France, pays | 2025 |
| `culture.frequentation_musees` | culture-frequentation-musees + COG | France, département | 2024 |

Dépense : fonction COFOG 08.2 « services culturels », toutes administrations publiques, hors audiovisuel public, édition et dépenses fiscales ; recalculée en millions d'euros sur le PIB pour éviter l'arrondi à 0,1 point d'Eurostat. Dépense et emploi culturel ont un sens neutre (choix politique, structure de l'économie).

Trous : fréquentation des monuments nationaux (le jeu du Centre des monuments nationaux sur data.gouv.fr s'arrête à 2022, non branché) ; l'ancien portail data.culture.gouv.fr redirige vers culture.data.gouv.fr, le fichier des musées est lu directement sur le stockage du ministère.

## Premiers constats

- Les administrations publiques françaises consacrent 0,646 % du PIB aux services culturels en 2024, contre 0,484 % en moyenne dans l'UE ; la France se classe au 9e rang, derrière l'Estonie (0,962 %) et Malte (0,943 %).
- Cette part a culminé à 0,717 % en 2013 avant de redescendre à 0,622 % en 2016 ; elle oscille depuis entre 0,62 et 0,65 %.
- L'emploi culturel représente 4,8 % de l'emploi en France en 2025 (4,3 % dans l'UE), contre 4,0 % en 2018, une hausse en partie due aux ruptures de série de 2021 et 2024.
- Les musées de France ont enregistré 71,2 millions d'entrées en 2024, au-dessus du niveau d'avant la crise sanitaire (65,9 millions en 2019) après une chute à 23,8 millions en 2020.
- Paris concentre 31,6 millions d'entrées en 2024 et les Yvelines (Versailles) 8,6 millions, soit à eux deux plus de la moitié du total national.
