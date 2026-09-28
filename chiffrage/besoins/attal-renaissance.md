# Besoins de barèmes : Gabriel Attal (Renaissance)

Coûts unitaires nécessaires pour chiffrer les mesures marquées `A_CHIFFRER` dans
`chiffrage/programmes/attal-renaissance.yaml`. Identifiants indicatifs ; reprendre ceux de `baremes.yaml` quand ils
existent. Montants en Md€ courants, régime de croisière 2032, référence législation au 1er janvier 2027.

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
