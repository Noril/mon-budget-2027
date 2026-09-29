# Barèmes complémentaires : Jean-Luc Mélenchon (La France insoumise)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/melenchon-lfi.yaml`) avait besoin, et indique lesquels figurent désormais dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 29 septembre 2026) : toutes les mesures du programme sont chiffrées ou classées non chiffrables ; aucune n'est en attente.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant entre parenthèses ou après la flèche est celui de la mesure concernée. Un paramètre « non inscrit » est sourcé directement dans la mesure : il pourrait devenir un barème commun. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

Paramètre transversal : le SMIC net cible est de 1 700 € en campagne 2026 et de 1 600 € dans L'AEC 2025. De nombreuses mesures y sont indexées : pensions minimales, AAH, garantie d'emploi, conscription.

## Retraites

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût en régime de croisière d'un an d'âge légal (64 → 60 ans), séparé de la durée d'assurance (43 → 40 ans), net des effets sur chômage, RSA et invalidité | retraite-60-ans | COR, rapport annuel et fiches de variantes ; DSS, étude d'impact de la LFRSS 2023 ; CNAV |
| Coût de la suppression de la décote | suppression-decote | COR ; DREES, « Les retraités et les retraites » |
| Coût d'un minimum de pension à X € net pour une carrière complète (MICO, retraites agricoles), stock et flux | pension-minimale-smic | DREES ; rapport Cour des comptes sur les minima de pension (2023) ; MSA |
| Écart salaires/prix × masse des pensions (1 % d'indexation) | indexation-pensions-salaires | Rapport CCSS ; PLFSS annexe B ; hypothèses SMPT/IPC du PSMT |
| Coût de la validation de trimestres au titre du RSA | trimestres-rsa | DREES (effectifs RSA) ; CNAV (AVPF, pour comparaison) |
| Rendement de 0,1 point de cotisation vieillesse ; assiette de l'intéressement, de la participation, de l'épargne salariale et des dividendes | hausse-cotisation-vieillesse | CCSS ; DARES (épargne salariale) ; INSEE, comptes des sociétés |

## Salaires, emploi, fonction publique

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût APU d'une hausse de 1 % du SMIC : allègements généraux, prime d'activité, masse salariale publique, retours de cotisations et d'impôts | smic-1700-net | Rapport du groupe d'experts SMIC ; DG Trésor ; CNAF (prime d'activité) |
| Coût brut et net d'un point de pourcentage de point d'indice, sur les trois versants | point-indice-10-pct, echelle-mobile-salaires | DGAFP, rapport annuel ; PLF, jaune « Rémunérations » |
| Masse salariale de l'Éducation nationale (enseignants du public et du privé sous contrat) | revalorisation-enseignants | MEN, RERS ; PLF programmes 140, 141, 139, 230 |
| Écart de coût entre un contractuel et un titulaire (CAS pensions compris) ; nombre de contractuels sur missions permanentes | titularisation-precaires-fp | DGAFP ; Cour des comptes (contractuels, 2020) |
| Coût complet annuel d'un emploi au SMIC dans le non-marchand ; nombre de chômeurs de longue durée | garantie-emploi, emploi-jeune-5-ans | DARES ; France Travail ; évaluation « Territoires zéro chômeur » (IGAS-IGF 2019) |
| Coût APU d'une semaine de congés supplémentaire (remplacements hospitaliers et autres) | sixieme-semaine-conges | DGAFP ; DREES (hôpital) |
| Recrutements nécessaires pour passer à 32 h les métiers pénibles ou de nuit du public ; coût des heures supplémentaires publiques | temps-travail-35h-32h | DGAFP ; DREES ; Cour des comptes (heures sup. police, hôpital) |
| Économies attendues des réformes de l'assurance chômage 2019-2025 | assurance-chomage-abrogation | Unédic, prévisions et études d'impact |

## Solidarités, logement, santé

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût d'une allocation différentielle au seuil de pauvreté à 60 % (adultes, jeunes de 18 à 24 ans hors foyer fiscal), et coût d'1 % de revalorisation des minima sociaux | garantie-autonomie | DREES, minima sociaux ; Ines (DREES-INSEE), simulations ; IPP |
| Coût d'une AAH au niveau du SMIC net | aah-smic | DREES ; PLF programme 157 |
| Coût d'1 % d'APL ; coût d'une ASF déconjugalisée | apl-10-pct, asf-deconjugalisee | CNAF ; PLF programme 109 |
| Coût d'une place d'hébergement d'urgence ; coût d'une place d'EHPAD public et d'un ETP soignant | zero-sans-abri, dependance-ehpad-publics | PLF programme 177 ; CNSA ; DREES |
| Coût du reste à charge public après AMO et du transfert des complémentaires (« 100 % Sécu ») | cent-pour-cent-secu | HCAAM (rapport 2022 sur l'articulation AMO-AMC) ; DREES, comptes de la santé |
| Rendement des franchises médicales et participations forfaitaires (hausse de 2024) | franchises-medicales | PLFSS 2024, étude d'impact ; CNAM |
| Coût chargé moyen d'un ETP soignant hospitalier ; coût d'un centre de santé | recrutement-soignants, centres-sante-deserts | DREES ; ATIH ; IGAS |
| Coût des protections périodiques (marché, remboursement) | protections-periodiques-gratuites | DREES ; rapport parlementaire sur la précarité menstruelle |
| Coût public d'un logement social neuf (subventions, aides de circulation, TVA réduite) | logements-publics-200000 | Bilan des logements aidés (DHUP) ; CDC ; Institut Montaigne 2022 |
| Coût public d'une rénovation globale et traitement en comptabilité nationale des prêts publics avec remboursement différé | renovation-700000-logements | ANAH ; DG Trésor ; INSEE (règles SEC 2010 sur les prêts) |
| Sinistralité et coût d'une garantie universelle des loyers | garantie-universelle-loyers | ANIL ; Action Logement (Visale) |
| Volume et prix d'une première tranche gratuite d'énergie et d'eau | premiere-tranche-gratuite-energie-eau | CRE ; SDES ; observatoire des services d'eau |

## Éducation, recherche, jeunesse, culture

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût de la gratuité de la cantine, des transports scolaires, des fournitures et du périscolaire (reste à charge des familles) | gratuite-ecole-cantine | CNAL ; DEPP ; Institut Montaigne 2022 ; Cour des comptes (restauration scolaire, 2020) |
| Nombre de repas scolaires et surcoût d'un repas 100 % bio | cantine-100-bio | Agence Bio ; Observatoire de la restauration collective ; Institut Montaigne 2022 |
| Coût d'une classe supplémentaire (enseignant chargé) et projection démographique des effectifs | classes-19-eleves | DEPP, projections ; PLF programmes 140 et 141 |
| Coût de la titularisation d'un AESH et de la fin de la mutualisation | aesh-fonctionnaires | PLF programme 230 ; rapport IGÉSR sur les PIAL |
| Coût d'investissement et de fonctionnement d'une place de crèche ; coût de la gratuité des crèches publiques | petite-enfance-500000-places | CNAF, observatoire de l'accueil du jeune enfant ; HCFEA |
| Droits d'inscription et CVEC perçus ; coût d'un logement CROUS | gratuite-enseignement-superieur | MESR ; CNOUS ; Cour des comptes (droits d'inscription, 2018) |
| Coût annuel d'un jeune en service de neuf mois au SMIC (classe d'âge, taux de participation, encadrement, permis) | conscription-citoyenne | INSEE (classes d'âge) ; Cour des comptes (SNU, 2024) ; Institut Montaigne 2022 |
| Coût du CIR (dépense fiscale) et part réaffectée à la recherche publique | suppression-cir, recherche-investissement | Voies et moyens tome 2 ; MESR ; Cour des comptes (CIR, 2021) |
| Dépenses culturelles publiques en % du PIB (périmètre du 1 %) ; budget du ministère des sports | culture-1-pct-pib, sport-1-pct-budget | DEPS (ministère de la Culture) ; PLF missions Culture et Sport |

## Écologie, énergie, transports, industrie, international

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Écart de l'investissement public vert au besoin (enveloppe du plan de 200 Md€, sans double compte) | plan-investissement-200-md, energies-renouvelables, plan-rail-fret, reconstruction-industrielle, agriculture-bio-installation | I4CE, panorama des financements climat ; rapport Pisani-Ferry-Mahfouz (2023) ; SGPE |
| Rendement d'1 €/MWh d'accise sur l'électricité ; niveau de l'accise avant la hausse de 2024-2025 | abolir-hausse-accise-electricite | Voies et moyens tome 1 ; CRE |
| Coût d'un bouclier sur les prix du gaz, de l'électricité et du carburant par € de prix bloqué | tarifs-reglementes-gaz, blocage-prix-energie-carburant | Cour des comptes (boucliers tarifaires 2022-2023) ; CRE ; DGEC |
| Recettes de TVA sur les transports publics | tva-transports-5-5 | GART ; Voies et moyens tome 1 |
| Flux de dividendes, péages et redevances des sociétés à renationaliser ; indemnités de résiliation des concessions autoroutières | renationalisations | APE, rapport annuel ; ART (autoroutes) ; Sénat, commission d'enquête autoroutes (2020) |
| Trajectoire de l'APD en % du RNB en loi de finances | aide-developpement-0-7 | PLF, document de politique transversale APD ; OCDE-CAD |
| Contribution française au budget de l'UE (PSR-UE) et solde net | contribution-ue | PLF, jaune « Relations financières avec l'UE » |
| Coût d'1 % de DGF | dotations-collectivites | PLF, jaune « Transferts aux collectivités » ; DGCL |
| Coût chargé moyen d'un ETP par ministère (justice, intérieur, services déconcentrés) | services-publics-proximite-postes, violences-sexistes-2-6-md | PLF, projets annuels de performance ; DGAFP |
| Trajectoire des crédits de défense dans la LPM en vigueur (point de référence, sans montant annoncé par le candidat) | defense-souveraine | LPM 2024-2030 ; PLF mission Défense |

## Recettes

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Rendement d'un ISF de type 2017 (barème, assiette, élasticité, exil) moins l'IFI ; assiette carbone du volet climatique | isf-climatique | Voies et moyens tome 1 ; France Stratégie, comité d'évaluation des réformes du capital ; CPO |
| Patrimoine des foyers au-delà de 100 M€ et au-delà d'1 Md€, impôt déjà payé, taux d'évasion | taxe-zucman-2-pct | Note de G. Zucman (2025) ; CAE, note n° 76 (2023) ; IPP ; Sénat, rapport sur la PPL Zucman (2025) |
| Bénéfices des multinationales localisables en France (impôt universel, formule de répartition) | impot-universel-zucman-multinationales | EU Tax Observatory ; CAE ; DG Trésor |
| Rendement de la suppression du PFU (dividendes et intérêts au barème) | suppression-flat-tax | France Stratégie (évaluation du PFU) ; Voies et moyens |
| Simulation d'un barème d'IR à 14 tranches et d'une CSG progressive | ir-14-tranches, csg-progressive | Modèles Openfisca, Ines et TAXIPP ; DGFiP, statistiques IR par tranche |
| Rendement des DMTG par tranche, comptage sur toute la vie, plafond à 12 M€ ; coût du pacte Dutreil | successions-heritage-maximal, pacte-dutreil | CAE, note n° 63 ; Cour des comptes (pacte Dutreil, 2025) ; Voies et moyens tome 2 |
| Rendement d'1 point d'IS par tranche de bénéfice ; dividendes versés ; rachats d'actions | is-progressif, taxe-dividendes-rachats | DGFiP ; Banque de France ; INSEE, comptes des sociétés |
| Rendement de la TTF française par point de taux et par assiette | taxe-transactions-financieres | Voies et moyens tome 1 ; AMF |
| Rendement de la contribution sur les superprofits (contribution temporaire de solidarité 2022-2023) | taxe-superprofits | Voies et moyens ; Cour des comptes |
| Rendement additionnel par ETP de contrôle fiscal | lutte-fraude-fiscale | DGFiP, rapport d'activité ; Cour des comptes (fraude fiscale) |
| Coût des dépenses fiscales ciblées (aérien, kérosène, taxe au tonnage, etc.) | niches-fiscales, fiscalite-ecologique-importations | Voies et moyens tome 2 ; I4CE (dépenses brunes) ; IGF |
| Coût des allègements généraux au-delà de 2 SMIC ; assiette des salaires au-delà d'un seuil | exonerations-cotisations-2-smic, surcotisation-hauts-salaires | CCSS ; DSS ; rapport Bozio-Wasmer (2024) |
| Coût de la défiscalisation et de la désocialisation des heures supplémentaires | heures-sup-fiscalisation | Voies et moyens tome 2 ; PLFSS annexe 5 |
| Rendement de la CVAE (avant suppression), de la CFE et des exonérations de TFPB | cvae-cfe-retablies | DGCL ; Voies et moyens ; OFGL |
| Rendement d'une taxe d'habitation sur les 20 % de ménages les plus aisés | taxe-habitation-aises | DGFiP ; rapport Richard-Bur (2018) |
| Rendement d'1 point de TVA à taux réduit ; assiette des biens de luxe | tva-premiere-necessite-luxe | Voies et moyens tome 1 ; INSEE (consommation par produit) |
| Rendement du versement mobilité, des redevances de l'eau et de la TSBA | fiscalite-locale-eau-mobilite | GART ; agences de l'eau ; DGAC |

## Paramètres hors barèmes communs : dépenses

| Paramètre | Valeur utilisée (mesures) | Statut dans `baremes.yaml` et source |
|---|---|---|
| SMIC net mensuel 2026 | 1 477,93 € (smic-1700-net, pension-minimale-smic) | Non inscrit : cité dans la dérivation de `aah_au_smic_cout` ; [service-public.gouv.fr](https://www.service-public.gouv.fr/particuliers/vosdroits/F2300) |
| Objectif de pension minimale pour une carrière complète au SMIC | 85 % du SMIC net (pension-minimale-smic) | Non inscrit : la disposition légale est citée comme source de `retraites_minimum_contributif_hausse_100e` ; [IPP](https://blog.ipp.eu/2023/02/09/au-dela-des-1200-euros-quelles-perspectives-de-reforme-pour-les-petites-pensions/) |
| Hypothèse centrale de productivité du COR | 0,7 % par an (indexation-pensions-salaires) | Non inscrit ; [IPP](https://www.ipp.eu/indexation-dans-les-regimes-de-retraite-par-points-comment-lire-les-hypotheses-du-dernier-rapport-du-cor/) |
| AAH, montant maximal | 1 041,59 € par mois (aah-smic) | Cité dans la dérivation de `aah_au_smic_cout`, sans identifiant propre ; [service-public.gouv.fr](https://www.service-public.gouv.fr/particuliers/vosdroits/F12242) |
| RSA, personne seule | 651,69 € par mois (garantie-autonomie) | Non inscrit ; [service-public.gouv.fr](https://www.service-public.gouv.fr/particuliers/vosdroits/F19778) |
| Facteur PIB nominal 2026→2032 | 1,1842 (toutes les mesures reprises du contre-budget 2026) | **Inscrit** : `facteur_pib_2026_2032` |
| Inflation cumulée 2028-2032 (déflateur) | 9,5 % (echelle-mobile-salaires) | **Inscrit** : borne basse de `inflation_cumulee_2027_2032` (+9,44 % de 2028 à 2032) |
| Rendement des franchises médicales avant et après le doublement de 2024 | 1,3 et 2,5 Md€ (franchises-medicales) | Non inscrit ; [Capital](https://www.capital.fr/economie-politique/securite-sociale-25-milliards-d-euros-l-an-dernier-la-cour-des-comptes-preconise-un-elargissement-des-franchises-medicales-1527164), reprenant la Cour des comptes (mai 2026) |
| Dépenses culturelles publiques | 0,9 % du PIB (culture-1-pct-pib) | Non inscrit ; Institut Montaigne 2022 |
| Coût chargé d'un ETP d'EHPAD public | proxy : barème soignant hospitalier (dependance-ehpad-publics) | **Inscrit** pour le proxy : `cout_soignant_hospitalier_charge` ; pas de barème propre à l'EHPAD (à documenter : CNSA, DREES) |
| Chiffrages de l'Institut Montaigne 2022 | Montants 2022 (garantie-emploi, sixieme-semaine-conges, garantie-autonomie, gratuite-ecole-cantine, cantine-100-bio, classes-19-eleves, petite-enfance-500000-places, conscription-citoyenne, cent-pour-cent-secu, logements-publics-200000, garantie-universelle-loyers, tarifs-reglementes-gaz, trimestres-rsa) | Non inscrit ; [Institut Montaigne](https://www.institutmontaigne.org/presidentielle-2022/jean-luc-melenchon/), à réactualiser en barèmes 2032 |
| Montants du contre-budget LFI 2026 (chiffrage du parti) | Voir chaque mesure (20 mesures, confiance faible) | Non inscrit ; [contre-budget](https://lafranceinsoumise.fr/wp-content/uploads/2025/10/Budget-2026_LFI_web_pages.pdf), à remplacer par des barèmes indépendants |

Barèmes désormais inscrits pour des mesures d'abord laissées non chiffrables : produit des droits d'inscription et de la CVEC (`droits_inscription_superieur`, gratuité du supérieur) ; dépense et bénéficiaires de l'ASPA (`aspa_depense`, minimum vieillesse au seuil de pauvreté). Toujours manquants : écart de coût entre contractuel et titulaire ; effectifs publics en horaires de nuit ou pénibles.

## Paramètres hors barèmes communs : recettes

| Paramètre | Valeur utilisée et source | Mesures | Statut dans `baremes.yaml` |
|---|---|---|---|
| Part de la recette mécanique conservée après évitement, pour une hausse de la fiscalité du capital du top 1 % | 0,26 (CAE, septembre 2025, via franceinfo : « perte de recette de 74 centimes sur chaque euro ») | taxe-zucman-2-pct, successions-heritage-maximal (bas) | Non inscrit |
| Rendement statique d'un impôt plancher de 2 % sur les patrimoines de plus de 100 M€ | 20 Md€ (fourchette 15 à 25) ; contre-budget LFI 2026 ; G. Zucman (via Wikipédia) | taxe-zucman-2-pct | Non inscrit |
| Recette d'un taux minimal d'IS de 25 % (pilier 2 étendu), France | 2,2 / 18,4 / 26,3 Md€ (Institut Montaigne 2022, d'après l'OCDE et l'EU Tax Observatory) | impot-universel-zucman-multinationales | Non inscrit |
| Rendement d'une contribution sur les montants distribués, par point | 0,66 Md€ par point (9,9 Md€ sur 2013-2017 à 3 %) ; IGF, via vie-publique.fr | taxe-dividendes-rachats | Non inscrit |
| Gain d'une suppression des allègements au-delà de 2 SMIC | 1,5 à 7 Md€ (Sénat, amendement n° 1029 au PLFSS 2026 ; groupe d'experts sur le Smic) | exonerations-cotisations-2-smic | Non inscrit |
| Coût de la suppression de la taxe d'habitation pour les 20 % de ménages les plus aisés | 7,8 Md€ (2023, Sénat, rapport PLF 2023) | taxe-habitation-aises | Non inscrit |
| Coût du crédit d'impôt recherche | 7,7 Md€ (2025, Sénat, rapport PLF 2025) | suppression-cir | Non inscrit |
| Dépenses fiscales rattachées aux DMTG (majorant du pacte Dutreil) | 4,5 Md€ (2025, Cour des comptes, tableau 22) | pacte-dutreil | Cité dans la dérivation de `dmtg_rendement`, sans identifiant propre |
| Rendement d'un point du taux de TVA de 5,5 % | 2,0 Md€ (2025, net ; DG Trésor, Trésor-Éco n° 371) | tva-premiere-necessite-luxe | **Inscrit en dérivation** de `tva_point_tous_taux` (5,5 % → 2,0 Md€) |
| Gain des cotisations sociales sur l'intéressement, la participation et l'épargne salariale | 6,9 à 9 Md€ (2022, Institut Montaigne) | hausse-cotisation-vieillesse | Non inscrit |
| Gain d'un alourdissement des droits de succession avec réaction de l'assiette | ≤ 5 Md€ (Fondation IFRAP, juin 2024, programme du NFP) | successions-heritage-maximal | Non inscrit |
| Gain d'un impôt sur le revenu à 14 tranches (barème hypothétique) | 4,7 Md€ (2022, Institut Montaigne) | ir-14-tranches | Non inscrit |
| Facteurs PIB 2024→2032 (1,2336) et 2017→2032 (1,580), en plus de 2025→2032 | — | plusieurs | **Inscrit** pour 2024→2032 et 2025→2032 (`facteur_pib_2024_2032`, `facteur_pib_2025_2032`) ; 1,580 cité dans la dérivation de `isf_retabli_gain_net`, sans identifiant propre |

Barèmes utiles non trouvés en source ouverte :
- part des employeurs publics dans l'assiette des cotisations vieillesse du régime général ;
- coût du pacte Dutreil après la LFI 2026 ;
- barème et rendement de la CVAE avant 2023 ;
- gain net des administrations publiques d'un retour sur la baisse de CFE industrielle, compensation comprise.
