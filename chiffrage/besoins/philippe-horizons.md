# Besoins de barèmes : Édouard Philippe (Horizons)

Coûts unitaires nécessaires pour chiffrer les mesures marquées `A_CHIFFRER` dans
`chiffrage/programmes/philippe-horizons.yaml`. Les identifiants proposés sont indicatifs ; reprendre ceux de
`baremes.yaml` quand ils existent. Montants en Md€ courants, régime de croisière 2032, référence législation au 1er janvier 2027.

## Fiscalité des entreprises
- Rendement 2027-2032 de chaque impôt de production : CVAE (et calendrier de suppression en vigueur), CFE, C3S, taxe foncière sur les propriétés bâties des entreprises, versement mobilité (PLF/Voies et moyens, DGFiP, Conseil des prélèvements obligatoires). → `impots-production-moins-50md`
- Inventaire chiffré des aides aux entreprises hors allègements généraux (dépenses fiscales, crédits budgétaires, exonérations ciblées) : rapport sénatorial 2025 sur les aides publiques aux entreprises, Cour des comptes, IGF. Nécessaire pour borner le gisement de 50 Md€. → `aides-entreprises-moins-50md`

## Retraites
- Économie d'un relèvement de l'âge légal d'un an (âge d'ouverture des droits), en régime de croisière et par année de montée en charge (COR, DSS, rapports réforme 2023). → `retraites-travailler-plus-longtemps`
- Coût de la suspension de la réforme 2023 et calendrier de la législation de référence au 1er janvier 2027.
- Masse des pensions de droit direct ; coût d'un point de sous-indexation ; rendement de l'alignement de la CSG des retraités (8,3 % → 9,2 %) ; rendement de la suppression ou du plafonnement de l'abattement de 10 % à l'IR (DSS, PLFSS, Cour des comptes). → `retraites-contribution-retraites`
- Masse des cotisations vieillesse (pour un scénario de dérivation de cotisations vers la capitalisation). → `retraites-capitalisation-10-15pct`

## Chômage, santé
- Économie d'une réduction d'un mois de la durée maximale d'indemnisation, par tranche d'âge ; nombre d'allocataires de 50-54 ans en fin de droits longs (Unédic, DARES). → `chomage-12-mois-moins-50-ans`
- Dépense d'indemnités journalières maladie ; part des arrêts courts (≤ 3 jours) ; économie d'un jour de carence supplémentaire d'ordre public, public et privé (Cour des comptes, CNAM, DGAFP). → `arrets-maladie-carence`
- Tendance de l'ONDAM dans la référence ; coût d'un point d'ONDAM. → `sante-stabiliser-depenses`

## Éducation, recherche, famille
- Masse salariale des enseignants (public, privé sous contrat), coût employeur d'une hausse de 1 % de la rémunération moyenne, taux de retour (cotisations et impôts). → `enseignants-plus-20pct`
- Coût annuel d'un étudiant en école d'ingénieur publique ; durée moyenne des études. → `ingenieurs-100000`
- Coût d'un dispositif de soutien scolaire (référence : devoirs faits, stages de réussite). → `soutien-scolaire-universel`
- Coût d'une demi-part supplémentaire pour le 2e enfant (IPP/OpenFisca, DGFiP : nombre de foyers à deux enfants, plafonnement du quotient familial). → `part-fiscale-deuxieme-enfant`
- Coût budgétaire d'un PTZ (crédit d'impôt par prêt) et nombre de naissances. → `ptz-chaque-naissance`
- Nombre de parents reprenant après un congé parental, salaire moyen ; coût d'un complément de 20 % sur 2 mois. → `temps-partiel-parental`
- Rendement des droits de mutation à titre gratuit sur donations ; élasticité aux abattements (réforme 2011-2012). → `donations-plafonds-hausse`

## Écologie, transports
- Montant du Fonds vert voté pour 2027 ; périmètre des fonds existants d'adaptation (fonds Barnier). → `fonds-vert-doublement`, `fonds-adaptation-2md`
- Coût d'un programme d'avion bombardier d'eau (développement, série). → `canadair-plans-adaptation`
- Crédits du plan fret ferroviaire en vigueur (programme 203, SNCF Réseau). → `fret-ferroviaire`

## Défense, État, justice
- Coût annuel moyen d'un réserviste opérationnel ; coût annuel d'un volontaire du service militaire volontaire (LPM, rapports parlementaires). → `reservistes-smv`
- Montant annuel de la LPM 2024-2030 actualisée et trajectoire 2031-2032. → `lpm-massification`
- Coût moyen chargé d'un ETP de la fonction publique d'État (pension incluse). → `fonction-publique-non-remplacement`
- Montant des amendes non recouvrées. → `amendes-prestations-sociales`
- Coût à la place d'un établissement pour mineurs (EPM, CEF). → `mineurs-narco-etablissements`

## Cadre
- PIB nominal 2027-2032 et solde public de référence (pour l'enveloppe `deficit-2pct-2032`).
