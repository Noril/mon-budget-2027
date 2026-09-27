# Démocratie et institutions

Participation électorale (ministère de l'Intérieur, Parlement européen), confiance dans les institutions (Eurobaromètre standard) et activité législative (données ouvertes de l'Assemblée nationale). Uniquement des mesures agrégées et institutionnelles : aucun indicateur ne porte sur un parti, une liste ou un élu, et les voix par candidat sont écartées dès la normalisation.

## Indicateurs

| Indicateur | Source | Maille | Dernière période |
| --- | --- | --- | --- |
| `democratie.participation_presidentielle` | interieur-presidentielle-departements + COG | France, département | 2022 |
| `democratie.participation_legislatives` | interieur-legislatives-departements + COG | France, département | 2024 |
| `democratie.participation_europeennes` | interieur-europeennes-departements + COG, pe-participation-europeennes | France, département, pays | 2024 |
| `democratie.confiance_parlement` | eurobarometre-standard-confiance | France, pays | 2026-S1 |
| `democratie.confiance_gouvernement` | eurobarometre-standard-confiance | France, pays | 2026-S1 |
| `democratie.confiance_justice` | eurobarometre-standard-confiance | France, pays | 2026-S1 |
| `democratie.lois_promulguees` | an-dossiers-legislatifs | France | 2025 |
| `democratie.delai_adoption_lois` | an-dossiers-legislatifs | France | 2025 |

Participation : premier tour, votants rapportés aux inscrits ; la valeur France inclut les Français de l'étranger (taux officiel). Confiance : part des personnes qui ont « plutôt confiance », par semestre de terrain (sondage d'environ 1 000 personnes par pays, marge de l'ordre de ± 3 points). La confiance dans le gouvernement a un sens neutre : elle mesure aussi le jugement sur l'équipe en place. Lois : hors lois autorisant la ratification d'accords internationaux.

Trous : présidentielle 2017 (publiée en XLS multi-onglets) et législatives antérieures à 2022 non branchées ; la XIVe législature (avant 2017) n'est pas branchée pour les lois ; le nombre d'amendements n'est pas suivi.

## Premiers constats

- La participation au premier tour des législatives passe de 47,51 % en 2022 à 66,71 % en 2024 (scrutin anticipé), sans rejoindre celle du premier tour de la présidentielle de 2022, 73,69 %.
- Aux européennes de 2024, la France vote à 51,49 %, un peu au-dessus de la moyenne de l'Union (50,74 %), loin de la Belgique (89,01 %, vote obligatoire) et de l'Allemagne (64,74 %) ; la participation française remonte depuis le point bas de 2009 (40,63 %).
- Les écarts territoriaux sont forts : au premier tour de la présidentielle de 2022, 80,81 % dans le Gers contre 36,16 % en Guyane ; aux européennes de 2024, 60,08 % en Lozère contre 9,35 % en Guyane.
- Au printemps 2026, 23 % des Français font plutôt confiance à leur parlement (37 % dans l'UE, 71 % en Suède) et 21 % à leur gouvernement (37 % dans l'UE), après un creux à 12 % et 9 % à l'automne 2025. La justice inspire confiance à 47 % des Français, contre 58 % en moyenne dans l'UE.
- Le Parlement a promulgué entre 40 (2018, 2024) et 65 (2021) lois par an hors accords internationaux ; le délai médian entre le dépôt d'un texte et sa promulgation atteint 247,5 jours en 2025, contre 150,5 en 2018.
