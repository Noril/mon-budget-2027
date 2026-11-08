# Barèmes complémentaires : David Lisnard (Nouvelle Énergie)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/lisnard-nouvelle-energie.yaml`) avait besoin, et indique lesquels figurent dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 8 novembre 2026) : toutes les mesures relevées sont chiffrées ou classées non chiffrables ; aucune n'est en attente, mais le candidat annonce une ventilation détaillée de ses économies en décembre 2026.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant après la flèche est celui de la mesure concernée. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

## Prélèvements sur les salaires et impôts de production
- Valeur d'un point de CSG d'activité, part déductible, retour d'impôt sur le revenu (barèmes `csg_point_activite`, `csg_taux_activite`, `csg_taux_activite_deductible`, `retour_ir_csg_deductible`). → `csg-activite-9-2-a-6-6`
- Masse des cotisations salariales par risque (vieillesse de base, complémentaires, chômage) pour borner une baisse de 90 Md€ hors CSG (CCSS, Urssaf, Agirc-Arrco) : non inscrit ; utile pour vérifier que l'enveloppe tient dans l'assiette. → `cotisations-salaires-120md`
- Rendement 2026-2032 des impôts de production autres que la C3S et la CVAE (CFE, taxe foncière des entreprises, versement mobilité, taxe sur les salaires) : pistes CPO, Voies et moyens, FIPECO. → `impots-production-40md`

## Retraites
- Distribution de la masse des pensions par tranche de pension totale (DREES, EIR 2020 ou plus récent), au-dessus de 2 000 et 2 200 € : fichier DREES inaccessible le 8 novembre 2026 ; paramètre `part` (0,50, seuil lu en brut) fixé par convention et à recouper. Pourrait devenir un barème commun (`pensions_part_masse_au_dessus_2200`). → `gel-pensions-plus-2200`
- Coût d'amorçage d'un étage de capitalisation obligatoire (un tiers des pensions à terme) : pistes COR, Institut Molinari (cité par le candidat), rapports sur les fonds de pension. → `capitalisation-obligatoire-collective`

## État, effectifs, santé
- Départs annuels de la fonction publique hors retraite (fins de contrat, démissions : le candidat cite 500 000 départs par an) : DGAFP, rapport annuel. → `suppressions-postes-400000`
- Dotation de l'assurance maladie aux ARS (en plus de la subvention de l'État) : non retrouvée. → `suppression-ars`
- Coût de formation d'un étudiant en médecine (université, stages, rémunération des externes et internes). → `medecine-doublement-etudiants`
- Effectifs des juridictions correctionnelles (magistrats du siège et du parquet, greffiers). → `justice-effectifs-correctionnels`
- Coût d'investissement et de fonctionnement d'une place de prison, et part du programme de 15 000 places déjà financée dans la référence. → `prisons-20000-places`

## Famille, fiscalité du patrimoine
- Coût du plafonnement du quotient familial (gain d'un déplafonnement total) : pistes Institut Montaigne (2016, retour au plafond d'avant 2013 ≈ 3 Md€), DGFiP. → `quotient-familial-deplafonnement`
- Droits de succession acquittés sur les transmissions d'entreprises hors pacte Dutreil. → `transmission-entreprises-exoneration`

## Paramètres hors barèmes communs

| Paramètre | Valeur utilisée | Statut dans `baremes.yaml` et source |
|---|---|---|
| `part` (masse des pensions au-dessus de 2 200 €) | 0,50 (0,40 à 0,60), seuil en brut | Non inscrit ; convention à partir de la DREES (EIR 2020) et du PLFSS 2027 ([Public Sénat](https://www.publicsenat.fr/actualites/politique/gel-des-retraites-au-dela-de-1280-euros-un-effort-necessaire-pour-ne-pas-creer-de-fracture-generationnelle-justifie-le-ministre-david-amiel)) |
| `subvention` (ARS) | 0,627 Md€ (PLF 2026) | Non inscrit, même paramètre que Reconquête ; [Sénat](https://www.senat.fr/rap/l25-139-331/l25-139-331_mono.html) |
| `gain_cae`, `depense_cae` (pacte Dutreil) | 1,4 et 2,5 Md€ (2018-2019) | Non inscrits, mêmes paramètres que Glucksmann ; [CAE, note n° 69](https://www.cae-eco.fr/staticfiles/pdf/cae-note069.pdf) |
