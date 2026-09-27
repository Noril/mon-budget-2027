---
id: equipes-soins-primaires-zones-sous-denses
type: proposition
titre: Une équipe de soins primaires, médecins et infirmiers, dans chaque zone sous-dense, financée à la place des aides à l'installation qui ne marchent pas
domaine: sante
axes: []
constats: [acces-generalistes, ald-sans-medecin-traitant]
indicateurs: [sante.pop_apl_mg_faible, sante.ald_sans_mt]
preuves:
  - chevillard-2020-maisons-de-sante
  - cour-des-comptes-2025-aides-installation
  - loussouarn-2019-asalee
  - laurant-2018-infirmiers-substitution
  - grobler-2015-zones-sous-dotees
cout: à chiffrer dans plan/ ; financement visé par redéploiement des aides fiscales à l'installation
arbitrages: []
statut: brouillon
---

## La proposition

Dans chaque bassin où la population vit majoritairement sous le seuil d'accès aux généralistes, l'État finance une équipe de soins primaires : une maison ou un centre de santé pluriprofessionnel, et des infirmiers qui prennent en charge le suivi des malades chroniques en coopération avec les médecins (sur le modèle d'Asalée et des infirmiers en pratique avancée).

Le financement vient en priorité des aides fiscales à l'installation, supprimées dans ces zones.

## Pourquoi

- **Le besoin est là, et il s'aggrave.** En 2024, {{ind:sante.pop_apl_mg_faible@1.1.0 | france | 2024}} de la population vit sous le seuil d'accès aux généralistes, contre {{ind:sante.pop_apl_mg_faible@1.1.0 | france | 2022}} en 2022 ([[acces-generalistes]]). Certains territoires cumulent les deux difficultés : dans le Cher, {{ind:sante.pop_apl_mg_faible@1.1.0 | departement=18 | 2024}} de la population vit sous le seuil et {{ind:sante.ald_sans_mt@1.0.0 | departement=18 | 2025}} des malades chroniques n'ont pas de médecin traitant ([[ald-sans-medecin-traitant]]).
- **Les maisons de santé attirent les jeunes généralistes**, surtout en périurbain peu doté, là où le constat est le plus aigu ([[chevillard-2020-maisons-de-sante]], évaluation causale).
- **Les aides fiscales seules n'ont aucun effet mesurable**, selon la Cour des comptes ; réorienter cette dépense vers l'exercice coordonné est sa propre recommandation ([[cour-des-comptes-2025-aides-installation]]).
- **Travailler avec une infirmière permet à un généraliste de suivre plus de patients comme médecin traitant, sans travailler plus**, et l'effet est concentré dans les zones les moins bien dotées ([[loussouarn-2019-asalee]]).
- **La qualité n'en souffre pas** : les soins primaires assurés par des infirmiers donnent des résultats de santé similaires ou meilleurs ([[laurant-2018-infirmiers-substitution]], revue systématique).

## Comment la déployer

Par vagues, comme une expérience évaluée : les bassins éligibles sont tirés au sort pour l'ordre de déploiement, et l'effet est mesuré sur les indicateurs `sante.pop_apl_mg_faible` et `sante.ald_sans_mt` contre les bassins pas encore servis. Critère de poursuite écrit d'avance.

## Objections les plus fortes

- **« Les maisons de santé ne font que déplacer les médecins d'un territoire à l'autre. »** L'évaluation compare à des territoires témoins, mais ne mesure pas un éventuel appauvrissement des voisins. À vérifier avant généralisation.
- **« Dans les marges rurales, ça ne suffit pas. »** C'est exact : l'effet y freine le déclin sans l'inverser ([[chevillard-2020-maisons-de-sante]]). La proposition ne règle pas seule le rural isolé.
- **« Les preuves d'attraction sont plus minces qu'annoncé. »** La revue Cochrane ne trouve aucune preuve fiable pour les leviers d'attraction en zone sous-dotée, faute d'évaluations rigoureuses ([[grobler-2015-zones-sous-dotees]]) ; l'évaluation française retenue est postérieure et quasi expérimentale, pas randomisée. D'où le déploiement par vagues évaluées.
- **« Les chiffres de la Cour des comptes viennent d'une communication de congrès. »** Ils ne sont repris ici que pour l'absence d'effet des aides fiscales, conclusion que la Cour assume dans sa synthèse ; l'effet des maisons de santé repose sur l'évaluation publiée de l'Irdes.

## Reste à faire

- Chiffrer le coût net dans `plan/` : coût des équipes moins aides fiscales supprimées.
- Rattacher la proposition à un axe de `VISION.md`.
- Trancher séparément la régulation de l'installation des médecins, qui a un effet fort chez les infirmières mais se transpose mal à une profession en pénurie.
