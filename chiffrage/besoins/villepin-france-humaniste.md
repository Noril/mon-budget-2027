# Barèmes complémentaires : Dominique de Villepin (La France humaniste)

Ce fichier recense les coûts unitaires et les paramètres dont le chiffrage du programme (`chiffrage/programmes/villepin-france-humaniste.yaml`) avait besoin, et indique lesquels figurent dans les barèmes communs (`chiffrage/baremes.yaml`). **Statut (état au 20 novembre 2026) : toutes les propositions du programme « Réussir à nouveau » (258 propositions, 25 chapitres) sont chiffrées ou classées non chiffrables ; aucune n'est en attente, mais aucune vérification indépendante n'a encore été faite.** Les listes par domaine sont les recherches menées, avec des pistes de sources (ce ne sont pas des sources citées : chaque paramètre retenu porte sa propre source dans la mesure qui l'utilise) ; l'identifiant après la flèche est celui de la mesure concernée. Montants en Md€ courants, régime de croisière 2032, référence : législation au 1er janvier 2027 (`chiffrage/REFERENCE.md`).

## Fiscalité et niches
- Liste et coût des niches sociales autres que les allègements généraux (exonérations ciblées, heures supplémentaires, apprentissage, outre-mer) : annexe 4 du PLFSS ; aujourd'hui seuls les allègements généraux entrent dans le plafond du périmètre. → `extinction-niches-fiscales-sociales`
- Distribution des droits de succession par montant d'héritage et par lien de parenté (DGFiP, enquête mutations à titre gratuit) : nécessaire pour chiffrer l'exonération jusqu'à 1 M€ en ligne directe et l'exonération des successions affinitaires. → `successions-exoneration-1m-progressivite`, `successions-affinitaires-100000`
- Part des donations dans le coût du pacte Dutreil (Cour des comptes, rapport de novembre 2025). → `dutreil-transmissions-vivant`
- Rendement de la contribution tarifaire d'acheminement sur l'électricité, part abonnement (CRE, rapports sur les tarifs d'acheminement). → `electricite-cfd-cta`
- Consommation de gaz par secteur et écart de prix gaz-électricité au kWh (SDES, bilan énergétique ; CRE, prix repère) : l'estimation indicative de l'encadrement du prix du gaz repose aujourd'hui sur une convention. → `encadrement-prix-gaz`

## Retraites et Fonds France
- Classement comptable (dans ou hors des administrations publiques) d'un Fonds France gérant des comptes individuels à rendement fixe : avis de l'Insee sur les fonds publics existants (Fonds de réserve pour les retraites). → `capitalisation-publique-15md`, `fonds-france-foncieres`

## Justice, sécurité, solidarité
- Prix de journée récent d'un centre éducatif fermé (projet annuel de performance de la mission Justice, programme 182) : le chiffrage utilise 661 € (2017). → `structures-educatives-fermees-15000`
- Coût par place d'hébergement généraliste (projet annuel de performance du programme 177). → `hebergement-30000-places`
- Effectifs de magistrats par habitant, France et moyenne européenne (CEPEJ). → `justice-securite-moyens`

## Santé, autonomie, culture
- Dépenses de prévention financées par les seules administrations publiques (hors prévention au travail payée par les employeurs) : DREES, comptes de la santé, fiche 23. → `prevention-sante-plus-50pct`
- Coût d'une prestation de compensation du handicap sans barrière d'âge (CNSA). → `pch-barriere-age-enfants`
- Nombre d'artistes éligibles à un revenu garanti (DEPS, ministère de la Culture). → `statut-artistes-revenu-1000`

## Paramètres hors barèmes communs

| Paramètre | Valeur utilisée | Statut dans `baremes.yaml` et source |
|---|---|---|
| `prix_journee` (centre éducatif fermé) | 661 € (2017) ; 690 € prévus en 2018 ; centre éducatif renforcé 563 € | Non inscrit ; [Sénat, rapport n° 726 (2017-2018)](https://www.senat.fr/rap/r17-726-1/r17-726-16.html) |
| `credits`, `parc` (hébergement, programme 177) | 3,0 Md€ ; 203 000 places (2026) | Non inscrits ; [Sénat, avis sur le PLF 2026](https://www.senat.fr/rap/a25-142-2/a25-142-2-syn.pdf) |
| `base` (dépenses de prévention) | 8,7 Md€ (2024) | Non inscrit ; [DREES, comptes de la santé 2025, fiche 23](https://drees.solidarites-sante.gouv.fr/sites/default/files/2025-12/CNS%20-%20Fiche%2023%20-%20Les%20d%C3%A9penses%20de%20pr%C3%A9vention.pdf) |
| `cout_smv` (service militaire volontaire) | 38 000 € par volontaire (2022) | Non inscrit, même paramètre que Philippe ; [Sénat, rapport n° 34 (2023-2024)](https://www.senat.fr/rap/r23-034/r23-034_mono.html) |
| `aide` (leasing social) | 7 000 € par véhicule | Non inscrit, même paramètre que Tondelier ; [L'argus](https://www.largus.fr/actualite-automobile/leasing-social-50-000-vehicules-electriques-subventionnes-mission-accomplie-3) |
| `part_deficit`, `palier`, `paliers` (niches) | 1/3 ; 35 Md€ ; 5 | Paramètres du programme ([chapitre 5](https://lafrancehumaniste.fr/programme/reussir-a-nouveau/chapitre-5.html)) |
