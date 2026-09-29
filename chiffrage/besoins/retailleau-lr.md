# Barèmes complémentaires : Retailleau (LR)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/retailleau-lr.yaml`) avait besoin, et indique lesquels figurent désormais dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 29 septembre 2026) : toutes les mesures du programme sont chiffrées ou classées non chiffrables ; aucune n'est en attente.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant entre parenthèses ou après la flèche est celui de la mesure concernée. Un paramètre « non inscrit » est sourcé directement dans la mesure : il pourrait devenir un barème commun. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

## Travail, cotisations, fiscalité des entreprises
- Masse salariale des heures supplémentaires (secteur privé) et taux de cotisations salariales et patronales effectifs sur ces heures, après réduction de 11,31 % et déduction forfaitaire (Acoss/Urssaf, Dares) → seuil zéro cotisation.
- Part des heures travaillées au-delà de 1 623 h par an (Rexecode, Dares ACEMO) ; heures entre 1 607 et 1 623 h.
- Rendement de 1 point de cotisations patronales (famille, maladie, FNAL, versement mobilité), après allègements généraux → baisse de 15 Md€.
- Rendement de 1 point de cotisation salariale / de CSG activité → restitution de 15 Md€ aux salariés.
- Rendement 2025-2026 de la C3S, de la CVAE (calendrier de suppression voté), du forfait social par assiette (participation légale, supra-légale, intéressement, PER), de la CFE sur les établissements industriels.
- Coût budgétaire d'un sur-amortissement de 40 % (référence 2015-2017, DG Trésor / Voies et moyens).
- Élasticité de l'IS à la baisse du coût du travail (pour décider si les « 4 Md€ » d'IS sont un retour direct).

## Protection sociale, chômage
- Masses 2026-2027 : RSA, prime d'activité, ASS (DREES, PLF) ; microsimulation du RIA (Ines/IPP) ou, à défaut, nombre d'allocataires × montant moyen.
- Distribution des ménages sans activité par total d'aides non contributives rapporté au SMIC net (plafond de 70 %).
- Fraude sociale estimée et taux de recouvrement (HCFiPS 2026, Cour des comptes).
- Unédic : dépenses d'indemnisation après rupture conventionnelle (durée moyenne, allocation moyenne), frontaliers (surcoût), chiffrage des règles de juin 2024 (Unédic 2024), effet d'une dégressivité au-delà de 3 000 € nets et d'un rechargement à 9 ou 12 mois.

## Retraites
- Coût ou gain d'un an d'âge légal et d'un an d'âge du taux plein (COR, DSS) ; effet d'une décote de 7 % par an entre 63 et 65 ans ; taux plein automatique à 65 ans contre 67 ans (nombre de départs à taux plein par âge).
- Cumulants emploi-retraite (effectifs, revenus), coût de la surcote par génération, masse de cotisations retraite et chômage des seniors ayant le taux plein avant l'âge légal.
- Dépense fiscale et sociale de l'épargne retraite et de l'épargne salariale (si capitalisation incitée) ; coût de transition si une part des cotisations est basculée.

## Famille
- Masses 2026 : allocations familiales, majoration pour âge, complément familial, ARS, bourses de collège et lycée, réduction d'impôt pour enfant scolarisé, SFT, avantage du quotient familial (plafonné) pour les enfants mineurs, part enfants du RSA et de la prime d'activité.
- Nombre de mineurs (Insee) et de familles de 3 enfants mineurs ou plus ; part des mineurs dont les parents ne remplissent pas la condition de cinq ans.
- Coût d'une semaine de congé indemnisé à 70 % du salaire plafonné ; naissances annuelles.
- Coût du crédit d'impôt famille par tranche de plafond ; aide employeur à la garde (exonération au-delà de 2 421 €).
- Encours et intérêts des crédits immobiliers des foyers avec enfants mineurs, par décile (Banque de France, ERFS).

## Logement, transmission
- Revenus fonciers et BIC meublé (assiette, bâti amortissable) ; coût d'un amortissement de 4 % (rapport Daubresse-Cosson, DLF).
- Coût du PTZ (crédit d'impôt, génération annuelle), nombre de logements neufs par an.
- Exonération d'IS des HLM (350 M€), APL étudiants par décile parental, coût de l'hébergement d'urgence généraliste et part occupée par des étrangers en situation irrégulière (Cour des comptes).
- Produit des DMTG (successions, donations), coût des abattements de dons (don familial de sommes d'argent), DMTG sur transmissions d'entreprises hors Dutreil.

## État, services publics
- Coût annuel moyen chargé d'un agent public (par versant) et nombre de départs à la retraite par an → 125 000 ou 250 000 non-remplacements.
- Commande publique (170 Md€) et gains d'achats constatés (DAE).
- Point de traitement enseignant : coût de +135 € et +300 € nets par mois par échelon (coût employeur, CAS Pensions), effectifs enseignants par échelon ; effet de la baisse démographique à taux d'encadrement constant (DEPP).
- APD : crédits de la mission APD et APD au sens CAD ; dépense AME (environ 1,2 Md€) et panier de soins (rapport Évin-Stefanini).
- Charges de service public de l'énergie pour les nouveaux contrats EnR (CRE, délibération annuelle) selon prix de marché.
- LPM : annuités 2027-2030 de la LPM actualisée adoptée contre la version +50 Md€ du Sénat.
- Coût à la place de CEF/EPM et coût journalier d'un détenu (justice des mineurs, courtes peines).

## Paramètres hors barèmes communs

Paramètres utilisés sans barème commun (sourcés dans la mesure) ou qui manquaient, et qui rendraient le chiffrage plus robuste.

| Paramètre | Contenu recherché | Statut dans `baremes.yaml` |
|---|---|---|
| `hs_exoneration_part_salariale` | Part salariale de l'exonération des heures supplémentaires : 2 306 sur 5 428 M€ (Cour des comptes, NEB 2026) ; heures par tranche annuelle (1 607-1 623 h, au-delà) | **Inscrit en partie** : `hs_exoneration_cout` (5,4 Md€, part salariale de 2,3 Md€ détaillée dans la dérivation) ; la répartition des heures par tranche n'est pas inscrite |
| `cotisations_patronales_non_contributives` | Rendement d'un point de cotisation famille, maladie, FNAL, versement mobilité après allègements | Non inscrit (`masse_salariale_privee` donne un ordre de grandeur brut de 7,4 Md€ par point, avant allègements) |
| `forfait_social_par_assiette` | Ventilation Acoss (participation légale, supra-légale, intéressement, PER, abondements) | Non inscrit |
| `cfe_etablissements_industriels` | Produit de la CFE des établissements industriels (DGFiP, REI) | Non inscrit |
| `logements_neufs_annuels` | Autorisations et mises en chantier (SDES, Sitadel) ; 379 222 logements autorisés en 2025 | Non inscrit |
| `unedic_ruptures_conventionnelles` | Dépense d'allocation et durée moyenne après rupture conventionnelle ; chiffrage Unédic des règles de juin 2024 | Non inscrit |
| `seniors_trimestres_complets_avant_age_legal` | Effectif et salaire des salariés éligibles (Cnav, DREES EIR) | Non inscrit |
| `cumul_emploi_retraite` | Cumulants, revenus d'activité et cotisations (DREES) ; flux de surcote | Non inscrit |
| `retraites_taux_plein_65_decote_7pct` | Simulation COR/Cnav d'un âge minimal de 63 ans avec décote de 7 % par an jusqu'à 65 ans et taux plein automatique à 65 ans | Non inscrit (barèmes voisins : `retraites_age_legal_1_an`, `retraites_duree_assurance_1_an`) |
| `dmtg_titres_hors_dutreil` | Droits de mutation sur les transmissions d'entreprises hors pacte Dutreil | Non inscrit (`dmtg_rendement` : 21,4 Md€ au total, dont ≈ 17,0 Md€ de successions, sans distinction du Dutreil) |
| `interets_emprunt_residence_principale_familles` | Foyers avec enfants mineurs accédants et intérêts payés (ERFS, Banque de France) | Non inscrit |
| `ptz_cout_generation` | Coût budgétaire d'une génération de prêts à taux zéro et part de l'ancien | Non inscrit |
| `revenus_fonciers_bati` | Revenus fonciers et BIC meublés, valeur du bâti loué (DGFiP) | Non inscrit |
| `hebergement_urgence_cout_place` | Coût d'une place d'hébergement d'urgence et part occupée par des étrangers en situation irrégulière (Cour des comptes) | Non inscrit |
| `cspe_contrats_futurs_enr` | Charges de service public prévisionnelles des contrats d'énergies renouvelables 2028-2032 (CRE) | Non inscrit |
| `enseignants_prive_sous_contrat` | Effectif et rémunération (programme 139) | Non inscrit |
| `apd_cad_mission` | APD au sens du CAD et crédits de la mission APD | **Inscrit** : `apd_part_rnb` (APD de 12,88 Md€ en 2025, 0,42 % du RNB ; mission APD de 3,67 Md€ au PLF 2026 citée dans les limites) |
