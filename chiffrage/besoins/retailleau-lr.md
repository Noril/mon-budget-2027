# Besoins de barèmes : Retailleau (LR)

Coûts unitaires et assiettes nécessaires pour chiffrer les mesures `A_CHIFFRER` de `programmes/retailleau-lr.yaml`.
Millésime cible : 2032 en euros courants, référentiel = législation au 1er janvier 2027.

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

## Barèmes à ajouter (phase 2)

Paramètres utilisés sans barème commun (sourcés dans la mesure) ou manquants, qui rendraient le chiffrage plus robuste :

- `hs_exoneration_part_salariale` : part salariale de l'exonération des heures supplémentaires (2 306 / 5 428 M€, Cour des comptes NEB 2026) ; heures supplémentaires par tranche annuelle (1 607-1 623 h, au-delà).
- `cotisations_patronales_non_contributives` : rendement d'un point de cotisation famille, maladie, FNAL, versement mobilité après RGDU.
- `forfait_social_par_assiette` : ventilation Acoss (participation légale, supra-légale, intéressement, PER, abondements).
- `cfe_etablissements_industriels` : produit de CFE des établissements industriels (DGFiP, REI).
- `logements_neufs_annuels` : autorisations et mises en chantier (SDES Sitadel ; 379 222 autorisés en 2025).
- `unedic_ruptures_conventionnelles` : dépense d'allocation et durée moyenne après rupture conventionnelle (Unédic) ; chiffrage Unédic des règles de juin 2024.
- `seniors_trimestres_complets_avant_age_legal` : effectif et salaire des salariés éligibles (Cnav, Drees EIR).
- `cumul_emploi_retraite` : cumulants, revenus d'activité et cotisations (Drees) ; flux de surcote.
- `retraites_taux_plein_65_decote_7pct` : simulation COR/Cnav d'un âge minimal 63 ans avec décote 7 %/an jusqu'à 65 ans et taux plein automatique à 65 ans.
- `dmtg_titres_hors_dutreil` : droits de mutation sur transmissions d'entreprises hors pacte Dutreil.
- `interets_emprunt_residence_principale_familles` : foyers avec enfants mineurs accédants et intérêts payés (ERFS, Banque de France).
- `ptz_cout_generation` : coût budgétaire d'une génération de PTZ et part de l'ancien.
- `revenus_fonciers_bati` : revenus fonciers et BIC meublés, valeur du bâti loué (DGFiP).
- `hebergement_urgence_cout_place` et part des places occupées par des étrangers en situation irrégulière (Cour des comptes).
- `cspe_contrats_futurs_enr` : charges de service public prévisionnelles des contrats EnR 2028-2032 (CRE).
- `enseignants_prive_sous_contrat` : effectif et rémunération (programme 139).
- `apd_cad_mission` : APD au sens du CAD et crédits de la mission APD.
