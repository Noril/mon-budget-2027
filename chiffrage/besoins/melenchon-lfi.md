# Besoins de barèmes : Jean-Luc Mélenchon (La France insoumise)

Ce fichier liste les coûts unitaires nécessaires pour chiffrer les 80 mesures `A_CHIFFRER` de `programmes/melenchon-lfi.yaml`. Les sources indiquées sont des pistes : chaque barème doit citer ses propres sources et son millésime. Les barèmes communs avec d'autres programmes (SMIC, point d'indice, âge de la retraite, ISF, successions…) sont à définir une seule fois.

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
