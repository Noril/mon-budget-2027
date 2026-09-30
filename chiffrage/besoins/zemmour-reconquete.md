# Barèmes complémentaires : Éric Zemmour (Reconquête)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/zemmour-reconquete.yaml`) avait besoin, et indique lesquels figurent désormais dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 29 septembre 2026) : toutes les mesures du programme sont chiffrées ou classées non chiffrables ; aucune n'est en attente.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant entre parenthèses ou après la flèche est celui de la mesure concernée. Un paramètre « non inscrit » est sourcé directement dans la mesure : il pourrait devenir un barème commun. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`). Entre parenthèses : mesures concernées. Plusieurs barèmes sont communs avec le RN (`besoins/le-pen-rn.md`) : même valeur pour les deux.

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

## Paramètres hors barèmes communs

| Paramètre | Valeur utilisée | Statut dans `baremes.yaml` |
|---|---|---|
| `fp_suppression_800000_postes` | 30 à 40 Md€ par an (François Ecalle, cité par franceinfo, septembre 2026) | Non inscrit |
| `preference_nationale_prestations` | IFRAP : 6 à 7 Md€ ; APL : 2,4 Md€ ; prestations familiales : 1,6 Md€ | Non inscrit (la part des foyers du RSA hors UE est le barème `rsa_part_foyers_hors_ue`) |
| Crédits du PLF 2026 (Sénat) | Programme 147 : 0,652 ; DPT Ville : 20,0 ; subvention Ademe : 1,06 (CP) ; France Travail : 1,16 ; ARS : 0,627 ; CESE : 0,034 ; Arcom : 0,051 ; presse : 0,178 ; aide juridictionnelle : 0,714 ; programme 177 : 3,071 ; AGFPN (État) : 0,035, en Md€ | Non inscrit (Anah, mission APD et audiovisuel public sont inscrits : `anah_credits_etat`, `mission_apd_credits`, `audiovisuel_public_dotation`) |

Devenus barèmes communs le 30 septembre 2026 (harmonisation des paramètres entre programmes, retirés du tableau) : `droits_succession_rendement`, `cfe_rendement`, `retour_is_impots_production`, `accise_gazole_taux` et accise_essence_taux (tarifs en vigueur depuis le 1er août 2025 : 60,75 et 69,02 c€/l), `carburants_volume_gazole_routier`, `carburants_volume_essence`, `tva_induite_accise_carburants_centime`, `csg_taux_activite`, `csg_taux_activite_deductible`, `rsa_part_anciennete_plus_3_ans`, `rsa_part_foyers_hors_ue`, `fraude_sociale_recouvree`, `ame_aide_urgence_vitale_economie`, `cspe_eolien_pv_hausse_annuelle`, `enr_soutien_annees_non_engagees_2032`, `anah_credits_etat`, `mission_apd_credits`, `audiovisuel_public_dotation`, `etudiants_droits_differencies_effectif`, `etudiants_droits_differencies_part_exoneree`, `etudiants_droits_differencies_montant_moyen`, `fp_salaire_brut_entrant`, `retraites_age_legal_reference_2032`.

Mesures laissées non chiffrables faute de données : part des cotisants épargnés par la retraite par capitalisation ; volume des éloignements visés par la « remigration » ; retour d'impôt sur le revenu de la suppression de la CSG déductible.
