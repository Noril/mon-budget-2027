# État et action publique

Ce que coûte l'action publique, où la France dépense plus que ses voisins, combien d'agents la produisent et avec quelle maturité numérique ; finances des départements. Aucune fiche de constat ni de proposition pour l'instant.

## Indicateurs

| Indicateur | Source | Mailles | Dernière période |
| --- | --- | --- | --- |
| `etat.depense_services_generaux` (GF01) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_defense` (GF02) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_ordre_securite` (GF03) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_affaires_economiques` (GF04) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_environnement` (GF05) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_logement_equipements` (GF06) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_sante` (GF07) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_loisirs_culture` (GF08) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_enseignement` (GF09) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.depense_protection_sociale` (GF10) | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.remuneration_agents_publics` | eurostat-gov-10a-exp | France, pays (UE27) | 2024 |
| `etat.agents_fp` | insee-effectifs-fonction-publique + COG | France, région, département | 2023 (31 décembre) |
| `etat.agents_fp_1000hab` | insee-effectifs-fonction-publique + insee-estimations-population + COG | France, région, département | 2023 |
| `etat.agents_fpe_1000hab` | idem, fonction publique de l'État | France, région, département | 2023 |
| `etat.agents_fpt_1000hab` | idem, fonction publique territoriale | France, région, département | 2023 |
| `etat.agents_fph_1000hab` | idem, fonction publique hospitalière | France, région, département | 2023 |
| `etat.emploi_public_part` | ocde-emploi-public | France, pays (25 États membres, OCDE) | 2024 |
| `etat.indice_gouvernement_numerique` | ocde-gouvernement-numerique | France, pays (OCDE) | 2025 |
| `etat.depenses_fonct_departements` | ofgl-departements-consolides + COG | France, département | 2025 |
| `etat.taux_epargne_brute_departements` | ofgl-departements-consolides + COG | France, département | 2025 |

Le total des dépenses publiques est `finances.depenses_publiques` (domaine finances). Les agrégats UE des indicateurs OCDE ne sont pas des séries Eurostat : ils sont codés `UE_OCDE` et calculés comme l'explique leur champ `construction`.

## Premiers constats

Valeurs lues dans les tables calculées (`data/indicateurs/`) le 27 septembre 2026 ; les fiches devront les appeler par `{{ind:…}}`.

- En 2024, les administrations publiques françaises dépensent 57,3 % du PIB, contre 48,9 % dans l'UE, soit 8,4 points d'écart (8,3 en sommant les dix fonctions arrondies). La moitié de cet écart vient de la protection sociale : 23,7 % contre 19,6 % (+4,1 points). Viennent ensuite la santé (8,9 % contre 7,3 %, +1,6 point) et le logement et les équipements collectifs (1,4 % contre 0,7 %, +0,7 point). Les sept autres fonctions pèsent ensemble 1,9 point.
- Les services généraux des administrations (GF01), qui comprennent le coût de l'administration générale mais aussi les intérêts de la dette, ne pèsent presque rien dans l'écart : 6,2 % du PIB contre 6,1 % dans l'UE. L'ordre public (1,8 % contre 1,7 %) est aussi dans la moyenne. L'écart vient donc des transferts et des services financés, pas de la machine administrative. Il s'est réduit depuis 2014 dans les affaires économiques (+1,1 point en 2014, +0,4 en 2024) et la protection sociale (+4,7, puis +4,1), mais creusé dans la santé (+1,2, puis +1,6).
- La rémunération des agents publics représente 12,4 % du PIB en 2024, contre 10,2 % dans l'UE et 8,3 % en Allemagne ; elle a baissé depuis 2014, où elle atteignait 13,1 %. Selon l'OCDE, les administrations emploient 20,9 % des actifs occupés en France en 2024, contre 16,5 % en moyenne dans les 25 États membres couverts, 11,9 % en Allemagne et 28,4 % en Suède ; cette part a baissé depuis 2014 (22,5 %).
- Fin 2023, la France compte 5,53 millions d'agents de la fonction publique hors militaires (5,19 millions fin 2011), soit 80,9 pour 1 000 habitants : 33,2 dans la fonction publique de l'État, 29,5 dans la territoriale, 18,2 dans l'hospitalière. Ce taux va de 50 dans l'Ain à 162 à Paris, siège des administrations centrales.
- Côté numérique, l'OCDE classe l'administration française au-dessus de la moyenne : indice de gouvernement numérique de 0,803 en 2025 (0,665 en 2022), contre 0,647 en moyenne simple de l'UE ; cinquième des 24 États membres couverts, derrière le Portugal, l'Estonie, l'Irlande et le Danemark. Dans les départements, les dépenses de fonctionnement sont passées de 896 € à 1 046 € par habitant entre 2019 et 2025. Leur taux d'épargne brute est tombé de 16,8 % en 2022 à 7,1 % en 2024, puis 9,1 % en 2025 ; 20 départements sur 96 sont sous 7 %, dont la Gironde (0,6 %).
