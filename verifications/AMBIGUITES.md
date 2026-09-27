# Définitions à préciser

Relevé par les vérificateurs le 27 septembre 2026. Aucune de ces ambiguïtés ne produit d'écart sur les données
actuelles ; chacune pourrait en produire à la prochaine livraison. À reporter dans le champ `construction`.

| Indicateur | À écrire explicitement |
| --- | --- |
| Toutes les séries Eurostat avec maille `pays` | Les agrégats (EU27_2020, EA20…) figurent dans la maille pays, à côté des États |
| `etat.agents_*_1000hab` | Filtrer GEO_OBJECT dans insee-estimations-population : « 01 » est l'Ain et la Guadeloupe |
| `etat.indice_gouvernement_numerique`, `etat.emploi_public_part`, `defense.*_otan`, `europe_international.apd_rnb` | Table complète de correspondance des codes pays (ISO3 ou nom anglais vers code Eurostat) |
| `etat.depenses_fonct_departements`, `etat.taux_epargne_brute_departements` | Métropole de Lyon et Paris exclues par `categ = DEPT` ; à revérifier si l'OFGL change sa nomenclature |
| `immigration.premieres_demandes_asile`, `immigration.taux_protection_*` | Liste exhaustive des codes exclus de la maille département (N/D, 9715, 20, « Autres départements ») |
| `education.ecart_dnb_ips` | Seuils de quartile calculés sur tous les collèges IPS valides, pas seulement ceux qui ont des résultats au brevet |
| `ecologie.tues_route` | La maille france vient de l'ONISR, pas de la ligne FR d'Eurostat |
| `logement.logements_autorises`, `logement.logements_commences`, `logement.prix_m2_logements` | Complétude des douze mois vérifiée par territoire ou au niveau national |
| `numerique.top500_puissance` | Part UE = somme des Rmax bruts des 27, puis un seul arrondi |
| `agriculture.revenu_agricole_reel` | Aucun filtre géographique (le jeu ne contient pas de régions NUTS) |
| `transports.part_modale_rail_*` | Égalité exacte sur TRN et RAIL, à distinguer des agrégats TRN_BUS_TOT_AVD et RAIL_IWW_AVD |
| `democratie.confiance_parlement` | Comparaison du libellé insensible à la casse (« PARLIAMENT » selon les vagues) |
