# Besoins de barèmes : Tondelier (Les Écologistes)

Coûts unitaires et assiettes nécessaires pour chiffrer les mesures `A_CHIFFRER` de
`programmes/tondelier-ecologistes.yaml`. Millésime cible : 2032 en euros courants, référentiel = législation au
1er janvier 2027. Plusieurs besoins sont communs avec `retailleau-lr.md` (cotisations, retraites, point d'indice,
enseignants) : un même barème pour les deux.

## Fiscalité du patrimoine et du capital
- Distribution des patrimoines au-delà de 100 M€ (nombre de foyers, patrimoine total, part de biens professionnels) et hypothèses d'évitement ou d'exil (CAE, IPP, Zucman 2025, Banque de France) → taxe Zucman.
- Rendement de l'ISF 2017 contre l'IFI ; élasticité d'assiette.
- Successions et donations : distribution des transmissions par tranche d'actif net (au-delà de 4 M€, au-delà de 13 M€), coût du pacte Dutreil, abattement assurance-vie (990 I), démembrement (CPO 2024, IPP).
- Rendement d'un point de PFU (part IR), d'un point de CSG sur les revenus du patrimoine et de placement, de la TTF par point de taux et d'assiette.
- IR : rendement d'une tranche à 60 % au-delà de 250 000 € (par part), coût d'une baisse des premières tranches.
- Taxe sur les services numériques : rendement par point et effet du seuil.
- IS : rendement d'un impôt minimal sur les groupes de plus de 1 Md€ de chiffre d'affaires (taxe « multinationales » débattue au PLF 2026), niche Copé.

## Cotisations, emploi, revenus
- Coût des allègements généraux par tranche de salaire (au-delà de 1,6 SMIC), coût des exonérations d'heures supplémentaires ; effet d'une désindexation.
- SMIC à 2 000 € brut : effet sur les allègements, la prime d'activité, la masse salariale publique, les cotisations et l'IR (DG Trésor, Dares).
- Point d'indice : coût de 1 % (trois fonctions publiques, CAS Pensions inclus) ; masses par catégorie (A, B, C).
- Rendement d'un point de CSG, et d'une CSG progressive.
- Unédic : économies des réformes 2019, 2021, 2023, 2025 (chiffrages Unédic), coût de l'indexation des allocations sur l'inflation.
- Coût d'un emploi en entreprise à but d'emploi (TZCLD), nombre de chômeurs de longue durée de 55 ans et plus.
- Coût d'une année de maintien de salaire pour les travailleurs des secteurs exposés (effectifs licenciés par an).

## Retraites, solidarité
- Coût d'un trimestre d'âge légal (retour de 62 ans 9 mois à 62 ans selon le référentiel post-suspension), carrières longues à 60 ans (COR, DSS).
- Minimum contributif et ASPA : effectifs et coût d'une hausse au seuil de pauvreté.
- Rendement de 0,2 point de cotisation vieillesse, d'un point déplafonné au-delà du PSS, d'un assujettissement de l'épargne salariale.
- RSA : allocataires, montant ; coût d'un passage à 50 % du SMIC net et de l'ouverture aux 18-24 ans fiscalement indépendants (Drees, Ines).
- APL : masse (environ 16 Md€), coût de +10 % ; RLS (environ 1,2 Md€).
- AAH : allocataires × 250 € × 12.
- Allocations familiales : coût d'un montant uniforme dès le premier enfant ; majoration à 14 ans.
- Congés : IJ maternité et paternité (coût d'un alignement à 16 semaines à 100 %), congé de naissance à 80 % sur 3 mois.
- Hébergement d'urgence : coût annuel d'une place.

## Santé, éducation, recherche
- Franchises et participations forfaitaires (rendement) ; transfert des complémentaires vers l'AMO (HCAAM 2022).
- Coût de fonctionnement public d'un centre de santé ; coût d'un poste d'infirmière scolaire.
- Enseignants : coût de +1 % de rémunération (public et privé sous contrat), coût d'un poste de professeur des écoles, nombre de classes du primaire et projection démographique (DEPP) pour 19 élèves par classe.
- Financement public de l'enseignement privé sous contrat (État et collectivités).
- Masse salariale de la recherche publique, crédits de fonctionnement des laboratoires ; CIR par taille d'entreprise.
- Bourses sur critères sociaux, CVEC, coût d'une place de logement étudiant (subvention publique).

## Climat, transports, logement
- MaPrimeRénov' : aide moyenne par rénovation d'ampleur, volume du référentiel ; aide unitaire par pompe à chaleur.
- Leasing social : aide publique par véhicule et part financée par CEE.
- Compensation publique d'un ticket mensuel unique (référence Deutschlandticket).
- Besoins de régénération ferroviaire (SNCF Réseau, conférence de financement 2025).
- Niches fiscales brunes (DGEC, I4CE, Cour des comptes) ; rendement du malus poids à 1 300 kg ; TSBA ; accise électricité et gaz par MWh.
- Concessions autoroutières : péages, échéances des contrats, coût d'entretien.
- Plan national d'adaptation : dépense publique actuelle (I4CE) pour déterminer le supplément.
- Budget UE : contribution française par point de RNB européen.
- APD : niveau 2026 en % du RNB, coût d'un point de base de RNB.

## Justice, sécurité, divers
- Coût complet d'un magistrat, d'un greffier, d'un attaché de justice ; créations prévues par la LOPJ.
- Programme 15 000 places de prison : crédits restants ; coût d'une journée de détention et d'une mesure de probation.
- Cannabis légal : recettes fiscales et économies de répression (CAE 2019).
- VSS : dépense publique actuelle (Fondation des femmes) pour le supplément de 3 Md€.

## Barèmes à ajouter (phase 2)

Paramètres utilisés dans `programmes/tondelier-ecologistes.yaml` hors de `baremes.yaml`, avec leur source ; à
transformer en barèmes communs (ils servent aussi à d'autres programmes) :

- `taxe_zucman_rendement` : 5 à 25 Md€ (Zucman 15-25 ; Aghion et al., d'après le CAE, environ 5). Source : https://fr.wikipedia.org/wiki/Taxe_Zucman (à remplacer par les notes originales du CAE et de Zucman).
- `abattement_10pct_pensions_cout` : 5,3 Md€ (bas 4,5, haut 5,7), 2025. Sources : https://lcp.fr/actualites/pensions-de-retraite-les-deputes-retablissent-en-commission-l-abattement-de-10-410270 et https://www.aladom.fr/actualites/secteur-service/11316/labattement-de-10-sur-les-pensions-histoire-dun-avantage-fiscal-que-personne-narrive-a-supprimer/ (Voies et moyens tome II à préférer).
- `cir_creance_totale` et part des grandes entreprises : 7,8 Md€ en 2023, 41 % pour les grandes entreprises. Source : https://www.financeinnovation.fr/2026/01/22/cir-le-credit-impot-recherche-cir-en-2023-la-creance-continue-daugmenter-tout-en-comptant-moins-de-declarants/ (MESRE).
- `allegements_au_dela_1_6_smic` : 2,7 à 5,5 Md€ (proxy Bozio-Wasmer) ; à refaire avec la RGDU 2026 (DSS).
- `smic_mensuel_brut` : 1 867,02 € (net 1 477,93 €) au 29 septembre 2026. Source : https://www.service-public.gouv.fr/particuliers/vosdroits/F2300.
- `rsa_montant_seul` 651,69 €, `aah_montant_max` 1 041,59 €, `aspa_montant_seul` 1 043,59 € (2026), service-public.gouv.fr (F19778, F12242, F16871).
- `minimum_vieillesse_allocataires` : 754 460 fin 2024 (Drees, via https://www.espace-social.com/minimum-vieillesse-le-nombre-de-beneficiaires-augmente-toujours-en-2024/).
- `seuil_pauvrete_60` : 1 288 € par mois en 2023. Source : https://www.insee.fr/fr/statistiques/8600989.
- `unedic_economies_reforme_2019_2021` : 2,3 Md€ par an (−0,8 conditions, −1,0 SJR, −0,5 dégressivité). Source : https://www.unedic.org/publications/evaluation-de-la-reforme-d-assurance-chomage-2019-2021. Manque : chiffrage de la réforme 2023 (contracyclicité) et des règles 2024-2025.
- `conge_paternite_cout_14_jours` : 522 M€ en 2022. Source : https://www.senat.fr/rap/l20-107-2/l20-107-28.html.
- `franchises_participations_rendement` : 2,5 Md€ en 2025 (Cour des comptes, via https://www.caducee.net/actualite-medicale/16965/franchises-medicales-a-140-euros-cumules-la-hausse-se-concentre-sur-les-plus-gros-consommateurs-de-soins.html).
- `enseignement_prive_financement` : 13,83 Md€ au total en 2022, dont État 8,5 et collectivités 1,9 Md€ (Depp). Source : dossier de presse de la mission d'information de l'Assemblée nationale.
- `taille_classes_premier_degre` : 21,3 (maternelle) et 20,7 (élémentaire), 16,7 en élémentaire d'éducation prioritaire, rentrée 2025 (DEPP) ; manque une projection démographique des effectifs du premier degré à 2032 (DEPP).
- `maprimerenov_ampleur` : 91 374 rénovations d'ampleur en 2024, aide moyenne 36 271 € (41 608 € pour les ménages modestes). Source : https://www.anah.gouv.fr/presse/bilan-2024-de-l-anah-un-effort-massif-pour-mieux-renover-les-logements.
- `rls_montant` : 0,9 Md€ (2026-2027), https://www.batiweb.com/actualites/legislation/budget-2027-allegements-bailleurs-sociaux-rls-49328.
- `leasing_social_aide` : 7 000 € (édition 2025, CEE) ; 13 000 € (édition 2024, budgétaire).
- `apd_part_rnb` : 0,50 % en 2024, 0,45 % attendu en 2025 (Sénat, rapport PLF 2025).
- `cannabis_recettes_legalisation` : 2,0 à 2,8 Md€ (CAE, note n° 52, 2019).
- `cout_greffier_charge` et `cout_attache_justice_charge` : absents (proxy utilisé : `cout_soignant_hospitalier_charge`) ; à lire dans le PAP du programme 166.
- `fp_part_categories` : 39 % A, 22 % B, 39 % C en 2023 (DGAFP) ; manque la part de la masse salariale par catégorie.
- Manquent aussi : rendement de la part IR du PFU, CEHR (1,5 Md€ en 2025, pour la tranche à 60 %), masse salariale au-delà du PSS, assiette de l'épargne salariale, masse salariale de la recherche publique, effectifs de la garantie d'autonomie à 18-24 ans, part de l'APD au sens CAD hors budget.
