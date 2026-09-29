# Barèmes complémentaires : Gabriel Attal (Renaissance)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/attal-renaissance.yaml`) avait besoin, et indique lesquels figurent désormais dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 29 septembre 2026) : toutes les mesures du programme sont chiffrées ou classées non chiffrables ; aucune n'est en attente.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant entre parenthèses ou après la flèche est celui de la mesure concernée. Un paramètre « non inscrit » est sourcé directement dans la mesure : il pourrait devenir un barème commun. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

## Prestations sociales et retraites
- Coût d'un point de revalorisation, par prestation indexée : pensions de base et complémentaires, prestations familiales, aides au logement, RSA, prime d'activité, AAH, minimum vieillesse (DSS, PLFSS, CNAF). Inflation prévue 2028. → `annee-blanche-2028`
- Répartition des pensions par montant (pour exclure les « petites retraites » : DREES, EIR). → `annee-blanche-2028`
- Économie annuelle de la réforme de 2023 à pleine montée en charge et calendrier de la législation de référence (suspension jusqu'en 2028). → `retraites-reprise-calendrier-2023`
- Naissances annuelles (INSEE). → `capitalisation-1000-euros-naissance`

## Travail, prélèvements
- Masse des cotisations salariales par tranche de salaire ; coût d'un point de cotisation salariale ; salariés au salaire médian (DSS, INSEE, Acoss). → `droit-au-brut-13e-mois`
- Inventaire chiffré des hausses du coût du travail depuis 2024 : refonte des allègements généraux (LFSS 2025-2026), aides à l'apprentissage, JEI, autres. → `cout-travail-hausses-2024`
- Rendement de la CVAE restant dû et calendrier de suppression en vigueur ; rendement des taxes créées depuis 2024 (contribution exceptionnelle sur les bénéfices des grandes entreprises, taxe sur les rachats d'actions…) et leur date d'extinction légale. → `cvae-suppression`, `taxes-dissolution-surtaxe-is`
- Économie de la réforme d'assurance chômage de 2024 (Unédic, DG Trésor). → `assurance-chomage-5md`
- Dépense d'indemnités journalières maladie. → `arrets-maladie`
- Coût de l'exonération des heures supplémentaires (IR et cotisations) et effet d'un relèvement de plafond. → `heures-supplementaires-defiscalisation`
- Coût des baisses d'IR ciblées (point de barème de la 1re/2e tranche). → `impots-classes-moyennes-2md`

## Fonction publique, collectivités, justice
- Coût moyen chargé d'un ETP (État hors ministères sanctuarisés, fonction publique territoriale) ; coût d'une indemnité de départ volontaire. → `fonctionnaires-moins-100000`
- Économies documentées des fusions de collectivités (Cour des comptes, fusions de régions 2016). → `collectivites-strate`
- Coût annuel chargé d'un magistrat et d'un greffier ; coût à la place de prison (construction, fonctionnement). → `justice-3000-magistrats-prisons`

## Éducation
- Nombre d'enseignants par échelon (public, privé sous contrat) ; coût employeur de 100 € nets/mois ; taux de retour. → `enseignants-200-500-euros`
- Nombre d'AESH et coût employeur de 100 € nets/mois. → `aesh-revalorisation-corps`
- Postes libérés par la baisse démographique 2027-2032 ; coût d'un poste de remplaçant. → `classes-moins-20-remplacants`
- Coût des groupes de niveau (heures postes) ; coût annuel d'un élève en année de transition. → `choc-des-savoirs-certificat`
- Nombre d'élèves ; coût unitaire annuel d'une licence d'assistant IA éducatif. → `assistant-ia-eleves`

## Innovation, formation, famille, énergie
- Crédits France 2030 et trajectoire au-delà de 2030. → `plan-ia-france-2040`
- Coût d'un crédit d'impôt à l'investissement numérique (référence : suramortissement numérique PME). → `credit-impot-productivite-ia`
- Coût unitaire d'une formation courte à l'IA ; part prise en charge par le CPF. → `formation-ia-20-millions`
- Coût de l'exonération des intérêts d'un livret réglementé (livret A) par Md€ d'encours ; coût de formation d'un professionnel de la petite enfance. → `garde-enfants-livret-200000`
- Montant des pensions alimentaires déclarées pour enfants et taux marginal moyen des bénéficiaires (DGFiP). → `pensions-alimentaires-defiscalisation`
- Coût d'un point de revalorisation du barème kilométrique ; coût du bonus électrique par véhicule d'occasion ; coût d'un boîtier E85. → `carburant-bareme-bonus-e85`
- Coût du dispositif Jeanbrun (référence) et d'un statut du bailleur privé élargi. → `logement-statut-bailleur-prive`

## Cadre
- PIB nominal 2027-2032 et solde public de référence (pour l'enveloppe `economies-120-150md`).

## Paramètres hors barèmes communs

| Paramètre | Valeur utilisée | Statut dans `baremes.yaml` et source |
|---|---|---|
| `masse_salariale_privee` | 740,0 Md€ (2025, assiette déplafonnée, Urssaf) ; un point de cotisation salariale ≈ 7,4 Md€ | **Inscrit** : `masse_salariale_privee` ([Urssaf](https://open.urssaf.fr/explore/dataset/masse-salariale-du-secteur-prive-france-entiere/)) |
| `salaire_brut_moyen_prive` | 3 602 €/mois (2024) | **Inscrit** : `salaire_brut_moyen_prive`, source INSEE Première du 23 octobre 2025 (la source secondaire utilisée d'abord est abandonnée) |
| `pensions_part_masse_sous_seuil` | 9,6 % (< 1 000 €), 15,4 % (< 1 200 €), 23,0 % (< 1 400 €) de la masse des pensions ; DREES, EIR 2020, calcul par milieux de tranche | Non inscrit ; [DREES](https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/4178_distribution-des-pensions-mensuelles/attachments/eir2020_distribution_des_pensions_mensuelles_xlsx) |
| `assurance_chomage_reforme_2024` | 3,6 Md€ (objectif du gouvernement, 2024) | Non inscrit (`assurance_chomage_depenses` ne donne que la dépense totale) ; [HuffPost](https://www.huffingtonpost.fr/economie/article/reforme-de-l-assurance-chomage-les-syndicats-et-le-patronat-parviennent-a-un-accord_242266.html), source secondaire |
| `pensions_alimentaires_defiscalisation` | 0,4 Md€ (séance du Sénat du 28 novembre 2025) | Non inscrit ; [Sénat](https://www.senat.fr/seances/s202511/s20251128/s20251128006.html) |
| `aesh_effectifs_cout` | 139 993 AESH, 3,16 Md€ ; revalorisation de 2023 : 240 M€ par an | Non inscrit ; [Sénat](https://www.senat.fr/rap/l25-139-313/l25-139-31310.html) |
| `prison_cout_place` | ≈ 400 k€ par place (construction), 100 à 150 € par jour de détention ; plan de 15 000 places : 5,7 Md€ | Non inscrit ; [Cour des comptes](https://www.ccomptes.fr/fr/publications/le-plan-15000-places-de-prison-une-ambition-forte-une-concretisation-laborieuse) |
| `cout_greffier_charge` | 62 900 € par ETPT (coût budgétaire complet) ; 23 300 € pour l'effet sur le solde des APU | **Inscrit** : `cout_greffier_charge` et `cout_greffier_apu` (PAP 2024, programme 166) |
