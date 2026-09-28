# Besoins de barèmes : Éric Zemmour (Reconquête)

Coûts unitaires à inscrire dans `chiffrage/baremes.yaml` pour chiffrer `programmes/zemmour-reconquete.yaml` (phase 2).
Montants en Md€ par an, régime 2032. Entre parenthèses : mesures concernées. Plusieurs barèmes sont communs avec le RN
(`besoins/le-pen-rn.md`) : même valeur obligatoire.

## Référence législative

- État de la réforme des retraites 2023 au 1er janvier 2027 (suspension jusqu'au 1er janvier 2028) et âge légal
  atteint en 2032 selon la législation (retraite-64-voire-65).

## Fiscalité

- Rendement de la CSG sur les revenus d'activité (salaires, indépendants) en 2032, distinct de la CSG sur revenus de
  remplacement et du capital (suppression-csg-activite).
- Rendement des droits de succession et des droits de donation en 2032 (suppression-droits-succession).
- Rendement des impôts de production : CFE, C3S, CVAE résiduelle, taxe foncière sur les propriétés bâties des
  entreprises, versement mobilité, taxe sur les salaires ; retour d'IS mécanique (suppression-impots-production).
- Rendement de l'accise sur les carburants (ex-TICPE) et TVA induite sur l'accise ; élasticité des volumes au prix
  (accise-carburants-moins-un-tiers).

## Retraites

- Gain d'un an d'âge légal supplémentaire (64 → 65 ans) en 2032 ; gain de la levée anticipée de la suspension
  (retraite-64-voire-65).

## Fonction publique

- Coût complet moyen d'un emploi public (rémunération + cotisations employeur, par versant) ; départs annuels en
  retraite hors enseignants, soignants, policiers, militaires (non-remplacement-800000-departs,
  gains-productivite-ia-administration).

## Prestations et immigration

- Dépense de prestations non contributives (RSA, prime d'activité, APL, allocations familiales, AAH, ASPA) versée à
  des étrangers (prestations-non-contributives-francais).
- Allocataires du RSA depuis plus de 3 ans « en capacité de travailler », montant moyen (rsa-limite-trois-ans).
- AME et soins urgents ; hébergement d'urgence des étrangers en situation irrégulière ; aide juridictionnelle versée
  aux étrangers ; visas délivrés (fin-ame, hebergement-urgence-irreguliers, aide-juridictionnelle-francais,
  hausse-cout-visas).
- Allocations chômage versées aux étrangers chômeurs depuis plus d'un an ; coût unitaire d'un éloignement
  (remigration-expulsions).
- Étudiants extra-communautaires et coût moyen d'un étudiant (etudes-payantes-etudiants-etrangers).

## Agences, dispositifs et transferts

- Charges de soutien aux EnR (commun RN) (fin-soutien-enr-intermittentes).
- Crédits de la politique de la ville : programme 147 et DPT (fin-politique-de-la-ville).
- Budgets d'intervention et de fonctionnement de l'Anah, de l'Ademe, des ARS, de France Travail (placement),
  de l'Arcom et des petites structures, du CESE et des CESER (suppression-anah, suppression-ademe, suppression-ars,
  france-travail-mise-en-relation, suppression-autres-agences-cese).
- Crédits budgétaires de l'APD (hors dépenses imputées et prêts) (suppression-aide-publique-developpement).
- Contribution française au budget de l'UE (commun RN) (contribution-ue-pre-covid).
- Dotations de l'audiovisuel public ; subventions aux associations, à la presse et aux syndicats
  (privatisation-audiovisuel-public, subventions-associations-presse-syndicats).
- Rendement documenté de la lutte contre la fraude sociale (fraude-sociale-delinquants).

## Barèmes à ajouter (phase 2 : paramètres sourcés utilisés faute de barème)

- `droits_succession_rendement` : 16,995 Md€ (PLF 2026, Sénat) ; 16,1 Md€ (2025, FIPECO).
- `cfe_rendement`, `impots_production_entreprises`, `is_retour_impots_production` : voir besoins/le-pen-rn.md.
- `accise_taux_carburants` : 59,40 c€/l gazole, 68,29 c€/l SP95-E5 (2026, FIPECO) ; volumes 34,7 et 14,8 Gl (SDES 2024).
- `fp_suppression_800000_postes` : 30 à 40 Md€ par an (François Ecalle, cité par franceinfo, septembre 2026).
- `preference_nationale_prestations` : IFRAP 6 à 7 Md€ ; RSA 15,6 % des foyers hors UE (2022) ; APL 2,4 Md€ ;
  prestations familiales 1,6 Md€.
- Crédits PLF 2026 (Sénat) : programme 147 0,652 ; DPT Ville 20,0 ; Anah 1,5 ; subvention Ademe 1,06 CP ; France
  Travail 1,16 ; ARS 0,627 ; CESE 0,034 ; Arcom 0,051 ; mission APD 3,67 ; audiovisuel public 3,878 ; presse 0,178 ;
  aide juridictionnelle 0,714 ; programme 177 3,071 ; AGFPN (État) 0,035.
- Étudiants étrangers : 108 100 relevant des droits différenciés, exonérations plafonnées à 30 % (2026-2027).
- Manquants : part des cotisants épargnés par la retraite par capitalisation ; volume des éloignements visés par la
  « remigration » ; retour d'IR de la suppression de la CSG déductible.
