# Barèmes complémentaires : Raphaël Glucksmann (Place publique)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/glucksmann-place-publique.yaml`) avait besoin, et indique lesquels figurent désormais dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 29 septembre 2026) : toutes les mesures du programme sont chiffrées ou classées non chiffrables ; aucune n'est en attente.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant entre parenthèses ou après la flèche est celui de la mesure concernée. Un paramètre « non inscrit » est sourcé directement dans la mesure : il pourrait devenir un barème commun. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

## Fiscalité et prélèvements

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Rendement d'1 point de CSG sur les revenus d'activité | baisse-csg-salaires | PLFSS / rapport CCSS ; LFSS annexe 3 |
| Droits de mutation à titre gratuit : rendement total et part de la tranche > 1,8 M€ en ligne directe ; élasticité de l'assiette | successions-tranche-haute-50 | Voies et moyens tome 1 ; CAE, note n° 63 « Repenser l'héritage » (2021) ; Fondation Jean-Jaurès |
| Coût fiscal du pacte Dutreil et part hors biens professionnels | successions-pacte-dutreil | Cour des comptes, évaluation du pacte Dutreil (2025) ; Voies et moyens tome 2 (dépense fiscale) |
| Plus-values latentes purgées au décès (montant annuel, rendement à un taux donné) | successions-plus-values-latentes | CAE note 63 ; IPP ; rapport du CPO sur la fiscalité du patrimoine |
| Accise sur l'électricité : rendement par €/MWh ménages, écart au niveau pré-février 2024 | annulation-hausse-accise-electricite-2024 | LFI 2024-2026, Voies et moyens ; CRE |
| Contribution sur les superprofits énergétiques (rendement de la contribution européenne 2022-2023 en France) | taxe-superprofits-fossiles | Voies et moyens ; rapport Cour des comptes sur la CRIS/contribution temporaire de solidarité |
| Rendement de l'exonération kérosène vols intérieurs, TVA sur billets, taxe jets privés / yachts, taxe poids lourds en transit | fin-niches-transport-polluant | Voies et moyens tome 2 ; I4CE ; rapport CGEDD eurovignette ; DGAC |
| Coût du CIR par taille d'entreprise (part des grands groupes, effet d'un plafond) | cir-plafonne-grands-groupes | MESR, données CIR ; Cour des comptes (2021) ; CNEPI |
| Rendement d'1 point de taxe sur les services numériques | hausse-taxe-gafam | Voies et moyens tome 1 |
| Aucun barème propre : enveloppe non détaillée, central = mesures identifiées (kérosène, CIR, Dutreil) sans double compte (règle 6) | suppression-niches-inefficaces | Voies et moyens tome 2 ; IGF revue des dépenses fiscales ; I4CE (niches brunes) |

## Salaires, fonction publique, prestations

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût APU d'une hausse du SMIC net de 1 % (allègements généraux, prime d'activité, masse salariale publique, retours de cotisations) | smic-1600-net | DG Trésor ; rapport du groupe d'experts SMIC ; DREES |
| Coût d'1 % de point d'indice (trois versants, net des retours) et inflation 2027-2032 | point-indice-indexe-inflation | DGAFP, rapport annuel ; PLF « Rémunérations » ; hypothèses d'inflation du PSMT/FMI |
| Masse salariale des enseignants (public + privé sous contrat), coût d'1 % | salaires-enseignants-10-pct | MEN, RERS ; PLF programmes 140, 141, 139, 230 |
| Coût moyen chargé d'un poste d'enseignant du premier degré ; suppressions de postes liées à la démographie en programmation | encadrement-eleves-primaire | PLF programme 140 ; DEPP projections d'effectifs |
| Coût d'un départ à 62 ans vs 64 ans (abrogation réforme 2023) en régime de croisière | abrogation-reforme-retraites-2023 | COR, rapport annuel ; DSS, étude d'impact PLFRSS 2023 ; CNAV |
| Économies attendues des réformes de l'assurance chômage 2019-2026 | abrogation-reforme-assurance-chomage | Unédic, prévisions et évaluations ; DARES |
| Coût d'un RSA ouvert aux 18-24 ans (effectifs éligibles, taux de recours) | minimum-social-unique-18-ans | DREES ; France Stratégie ; IPP |
| Coût par emploi TZCLD (contribution au développement de l'emploi) et nombre d'entrées | territoires-zero-chomeur | Fonds ETCLD ; IGF-IGAS évaluation (2019) ; DARES |
| Coût de l'AJPA et population cible d'une indemnité d'aidant | indemnite-proche-aidant | CNAF ; DREES enquête aidants |
| Coût unitaire du chèque énergie (bénéficiaires, montant moyen) et population « classes moyennes » à définir | cheque-carburant-energie-triple | DGEC ; ASP ; PLF programme 345 |
| Effectifs et coût par agent (soignants, police-gendarmerie, justice) pour une hypothèse de revalorisation | revalorisation-soignants-police-justice | DGAFP ; PLF missions Sécurités et Justice ; ONDAM |

## Jeunesse, éducation, culture

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Coût par volontaire-mois du service civique (indemnité, encadrement, protection sociale) × classe d'âge | service-civique-obligatoire | Agence du service civique ; Cour des comptes (SNU 2024, service civique) ; INSEE (classe d'âge) |
| Coût moyen d'un séjour collectif (colonie, classe découverte) et part publique | colos-pour-tous | DJEPVA, Pass colo ; CNAF ; Observatoire des vacances et des loisirs des enfants |
| Coût moyen d'une rénovation thermique d'école au m² et parc concerné ; part État / collectivités | plan-batisseurs-ecoles | Banque des territoires (EduRénov) ; Cour des comptes bâti scolaire ; CEREMA |
| Coût des bourses sur critères sociaux (base de remplacement par un capital formation) | capital-formation-universel | PLF programme 231 ; CNOUS |
| Coût de la part individuelle du pass Culture | pass-culture-part-individuelle | PLF programme 361 ; Cour des comptes (pass Culture 2024) |

## Transports, énergie, logement

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Aide publique par contrat de leasing social et nombre de ménages éligibles (< 2 000 €/mois, > 30 km/jour) | leasing-social-voiture-electrique | DGEC / ASP, bilan leasing social 2024-2025 ; INSEE mobilités domicile-travail |
| Enveloppe MaPrimeRénov' (2024 vs législation 2027) | maprimerenov-relance | PLF programme 174 ; ANAH rapports |
| Besoin de régénération SNCF Réseau non financé | plan-rail | Contrat de performance SNCF Réseau ; COI ; Cour des comptes |
| Coût d'un abonnement national à tarif fixe (compensation par titre, élasticité) | ticket-climat | Deutschlandticket (évaluations VDV) ; GART |
| Soutien public aux ENR (CSPE) dans la PPE 3 | plan-enr-reseaux | CRE, délibération charges de service public ; PPE |
| Coût d'un fonds foncier / aide à la pierre par logement social | logement-abordable-fonds-foncier | FNAP ; PLF programme 135 ; Cour des comptes |

## Santé, égalité, international, défense

| Barème | Mesures | Source publique suggérée |
|---|---|---|
| Budget actuel VSS (base du milliard supplémentaire) | plan-violences-sexistes-1-md | Document de politique transversale « Égalité femmes-hommes » ; Fondation des femmes |
| APD en % du RNB et RNB projeté 2027-2032 | aide-publique-developpement-0-7 | OCDE CAD ; PLF mission APD ; INSEE comptes nationaux |
| Dépense de prévention (hors ONDAM, fonds territorial) | prevention-sante-hors-ondam | DREES comptes de la santé |
| LPM en vigueur, coût de la réserve opérationnelle par réserviste, aide à l'Ukraine | defense-reserve-industrie-ukraine | LPM 2024-2030 et actualisation ; Cour des comptes (réserves 2024) |

## Paramètres hors barèmes communs

| Paramètre | Valeur utilisée | Statut dans `baremes.yaml` et source |
|---|---|---|
| SMIC net mensuel au 1er juin 2026 | 1 477,93 € (smic-1600-net) | Non inscrit : cité dans la dérivation de `aah_au_smic_cout` ; [compta-online](https://www.compta-online.com/smic-horaire-montant-mensuel-brut-net-ao1021) (arrêté du 22 mai 2026) |
| Déflateur cumulé 2027-2032 et facteurs PIB 2026→2032 et 2027→2032 | 1,1104 ; 1,1842 ; 1,1570 | **Inscrit** : `inflation_cumulee_2027_2032` (+11,03 %, produit exact 1,1103), `facteur_pib_2026_2032`, `facteur_pib_2027_2032` |
| Part des prélèvements revenant aux APU sur une hausse de rémunération publique | 25 % | **Inscrit** : `retour_prelevements_salaires_publics` (0,28 ; bornes 0,25 et 0,32) ; 25 % en est la borne basse |
| Économie de la réforme 2023 de l'assurance chômage (pleine charge 2027) | 4,5 Md€ par an | Non inscrit ; [Unédic](https://www.unedic.org/publications/reforme-2023-premiers-effets-de-la-reforme-de-contracyclicite) |
| Économie de la réforme 2019-2021 de l'assurance chômage | 2 à 2,3 Md€ par an | Non inscrit ; [AEF info](https://www.aefinfo.fr/depeche/648868-chomage-on-evalue-leffet-de-la-reforme-entre-2-et-23-md-en-rythme-de-croisiere-christophe-valentie-unedic), audition Unédic |
| Chèque énergie : foyers bénéficiaires (4,5 M), éligibles (6 M), montant moyen (153 €) | voir colonne précédente | Non inscrit ; [Connaissance des énergies](https://www.connaissancedesenergies.org/questions-et-reponses-energies/quest-ce-que-le-cheque-energie), [Sud Radio](https://www.sudradio.fr/sud-radio/cheque-energie-2026-montants-criteres-et-nouveautes-pour-les-menages) |
| Rendement d'1 €/MWh d'accise sur l'électricité (tous consommateurs) | 0,2 Md€ | **Inscrit** : `accise_electricite_1_euro_mwh` retient 0,30 Md€ (0,16 pour les seuls ménages, 0,33 avec la TVA induite), en remplacement de la valeur de 0,2 Md€ tirée d'une tribune de 2024 |
| Droits de succession seuls (PLF 2026) | 17,0 Md€ | **Inscrit en partie** : dérivation de `dmtg_rendement` ; manque la répartition des droits par tranche (DGFiP) |
| Exonération Dutreil réduite à 50 % ; coût du Dutreil 2018-2019 ; dépense 2022-2024 | 1,4 Md€ ; 2 à 3 Md€ ; 2,0 / 3,3 / 5,5 Md€ | Non inscrit (dépenses fiscales rattachées aux DMTG : 4,5 Md€ en 2025, citées dans `dmtg_rendement`) ; [CAE, note n° 69](https://www.cae-eco.fr/staticfiles/pdf/cae-note069.pdf), [Cour des comptes 2025](https://www.ccomptes.fr/sites/default/files/2025-11/20251118-Synthese-Pacte%20Dutreil.pdf) |
| Coût de la purge des plus-values latentes | 0,05 % du PIB (≈ 1,3 Md€) ; proposition de loi IGS : 9 Md€ (statique) | Non inscrit ; [CAE, note n° 69](https://www.cae-eco.fr/staticfiles/pdf/cae-note069.pdf), [Sénat](https://www.senat.fr/leg/exposes-des-motifs/ppl25-190-expose.html) |
| Indemnité de service civique | 504,98 € net (État), tutorat 100 €, prestation d'accueil 114,85 € | Non inscrit ; [barème de l'Agence du service civique 2026](https://www.service-civique.gouv.fr/api/media/assets/document/asc-indemnites-et-cotisations-01012026.pdf) |
| Budget du service civique 2026 | 465 M€ (110 000 volontaires) | Non inscrit ; [Sénat, avis PLF 2026](https://www.senat.fr/rap/a25-144-62/a25-144-62_mono.html) |
| Cohorte d'âge (naissances 2014) | 818 565 | Non inscrit ; [INSEE](https://www.insee.fr/fr/statistiques/2381380) |
| APD en % du RNB | 0,48 % en 2024 ; 0,38 % en 2026 | **Inscrit en partie** : `apd_part_rnb` (0,48 % en 2024, 0,42 % en 2025, OCDE, base CAD) ; le 0,38 % de 2026 vient d'une source secondaire ([Alternatives économiques](https://www.alternatives-economiques.fr/aide-au-developpement-la-france-s-eloigne-de-son-objectif-au-detriment-des-pays-les-plus-pauvres_04)) et n'est pas inscrit |
| ETPT enseignants du public (programmes 140 et 141) | 793 863 | **Inscrit en partie** : somme des ETPT cités dans la dérivation de `cout_enseignant_charge` (341 897 + 451 966) ; manque l'effectif du privé sous contrat (programme 139) |
