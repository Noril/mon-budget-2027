# Législation de référence du chiffrage

Toute mesure est chiffrée par rapport au **droit voté au 29 septembre 2026**, supposé inchangé jusqu'en 2032
(y compris ses calendriers déjà inscrits dans la loi). Le projet de loi de finances pour 2027, pas encore voté, n'en
fait pas partie. Une promesse qui reprend ce que prévoit déjà la loi coûte zéro ; une promesse qui annule une
mesure prévue par la loi coûte ce que rapporte cette mesure.

| Sujet | État du droit retenu | Source |
| --- | --- | --- |
| Retraites | Réforme de 2023 suspendue jusqu'au 1er janvier 2028 (LFSS 2026, loi n° 2025-1403 du 30 décembre 2025) : âge légal gelé à 62 ans et 9 mois, 170 trimestres pour la génération 1964 ; la montée vers 64 ans et 172 trimestres reprend le 1er janvier 2028. « Abroger la réforme de 2023 » coûte donc l'écart entre 62 ans et le calendrier repris en 2028, pas le coût du gel déjà voté. | [solidarites.gouv.fr](https://solidarites.gouv.fr/loi-de-financement-de-la-securite-sociale-2026-les-mesures-phares), [CMS](https://cms.law/fr/fra/legal-updates/la-loi-de-financement-de-la-securite-sociale-pour-2026-est-promulguee) |
| CVAE | Taux 2024 maintenu jusqu'en 2027, puis baisse et suppression en 2030 (LFI 2026, promulguée le 19 février 2026). Promettre la suppression de la CVAE ne coûte que l'avance sur ce calendrier. | [economie.gouv.fr](https://www.economie.gouv.fr/entreprises/gerer-sa-fiscalite-et-ses-impots/loi-de-finances-2026-ce-qui-change-pour-les-entreprises) |
| Contribution exceptionnelle sur les bénéfices des grandes entreprises | Prolongée pour l'exercice 2026 seulement (payée en 2027) ; éteinte ensuite. La pérenniser est une recette nouvelle à partir de 2028. | [LégiFiscal](https://www.legifiscal.fr/actualites-fiscales/4402-plf-2026-49-3-maintien-contribution-exceptionnelle-benefices-grandes-entreprises.html) |
| Autres mesures des LFI et LFSS 2026 | En vigueur telles que votées, y compris les censures du Conseil constitutionnel. Un contre-budget 2026 qui annule une ligne du PLF 2026 n'a d'effet que si cette ligne a été votée : à vérifier au cas par cas dans les textes promulgués. | [Lextenso](https://www.labase-lextenso.fr/breves/loi-de-financement-de-la-securite-sociale-pour-2026-BREVEBO193) |
| Dépenses | Pas de « tendanciel » propre au chiffrage : les coûts s'ajoutent à la trajectoire de référence de `plan/` (solde primaire gelé, ou FMI). | `plan/README.md` |

## Indexations : droit constant

Les montants sont mesurés à **droit constant**, pas contre la trajectoire de `plan/` :

- **Point d'indice** : aucune règle d'indexation dans la loi, donc gelé en référence. Promettre de l'indexer sur
  l'inflation coûte la masse indiciaire × l'inflation cumulée 2027-2032 (déflateur du FMI, `plan/hypotheses.yaml`) ;
  une « échelle mobile » des salaires publics aussi. Un gel promis coûte zéro.
- **Pensions et prestations** : indexées sur l'inflation selon la loi (code de la sécurité sociale). Promettre
  cette indexation coûte zéro ; une sous-indexation (« année blanche ») est une économie ; une indexation sur les
  salaires est un coût (écart salaires − prix).
- **Barèmes fiscaux** : l'indexation de l'IR n'est pas automatique ; la référence retient l'usage constant d'une
  indexation sur l'inflation (coût nul), un gel est donc une recette.
- **Effet 2032 d'une mesure temporaire ou d'une avance de calendrier** (suppression anticipée de la CVAE, par
  exemple) : `effet_solde_primaire.annuel` porte les montants année par année.

Ce choix rend les chiffrages comparables entre programmes. La trajectoire de référence de `plan/` (solde primaire
gelé en points de PIB) n'est pas « à droit constant » : l'écart est une limite connue de l'agrégation.

Points à trancher : les dispositions exactes des LFI et LFSS 2026 sur les allègements généraux, les APL des
étudiants étrangers et la prime carburant ; relevées par les agents de collecte, elles sont vérifiées mesure par
mesure et la lecture retenue est écrite dans `interpretation`.
