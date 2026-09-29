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

## Conventions communes de chiffrage (barèmes harmonisés, 29 septembre 2026)

Elles s'appliquent à tous les programmes ; le détail et les sources sont dans `baremes.yaml`.

1. **Salaires publics et postes.** Les cotisations employeurs (CAS Pensions, CNRACL, maladie, famille) vont à
   d'autres administrations publiques : elles ne comptent pas pour le solde (FIPECO). Effet sur le solde =
   rémunération brute hors cotisations employeurs × (1 − `retour_prelevements_salaires_publics`, 0,28). Pour un
   poste créé ou supprimé, utiliser les barèmes `cout_*_apu` (coût d'un entrant) ; pour revaloriser les agents en
   place, le salaire moyen (haut des barèmes `_apu`). Les barèmes `cout_*_charge` sont des coûts budgétaires de
   l'État, à ne plus utiliser pour le solde.
2. **Point d'indice.** Gelé à droit constant ; aucune projection par le PIB. Hausse ponctuelle de x % :
   x × `point_indice_1pct_2032` brut, × 0,72 en net. Indexation 2027-2032 : `indexation_point_indice_2027_2032`
   (28,6 brut, 20,6 net), montée en charge 0,13 / 0,30 / 0,48 / 0,66 / 0,83 / 1. Hausse de x % plus indexation :
   les deux, plus l'effet croisé x × 28,6. Les pensions induites vont dans le bas.
3. **Pensions.** Effet net = brut × (1 − `retour_prelevements_pensions`, 0,14) ; petites pensions 0,08 ; minima
   (ASPA, AAH, RSA) sans retour.
4. **Retraites (âge, durée).** Le central porte sur le solde du système de retraite. Le coût pour l'ensemble des
   administrations (Cour des comptes, DG Trésor), qui ajoute surtout les prélèvements sur l'emploi des seniors,
   relève d'un effet d'activité exclu par la règle 3 : il va dans `effets_retour` ou `chiffrages_tiers`.
5. **CSG.** Une baisse d'un point de CSG déductible rend 10 à 15 % en impôt sur le revenu (convention) : net
   ≈ 10,3 Md€ par point d'activité en 2026.
6. **Accise carburants.** 0,54 Md€ par centime et par litre avec la TVA induite (chiffre pour le solde).
7. **Smic.** Pour une hausse de 10 % ou plus, le produit linéaire de `smic_1pct_cout_apu` est un minorant.
8. **Minimum contributif.** Linéaire seulement jusqu'à 100-150 € de hausse.
9. **Cotisation vieillesse.** La valeur dépend du type de cotisation (voir le barème).
10. **Aide publique au développement.** En % du RNB (`rnb_nominal_2032`), et c'est un majorant : l'APD au sens
    de l'OCDE n'est pas qu'une dépense budgétaire.
11. **Projection en euros 2032.** Barèmes `facteur_pib_<année>_2032` pour les montants qui suivent l'activité ;
    pas de projection pour ce qui est gelé à droit constant.
12. **Lectures communes des bornes.**
    - Postes créés ou supprimés : entrant (`cout_*_apu`) au central, agent moyen (haut du barème) dans la borne
      défavorable au solde.
    - Revalorisation ciblée d'agents en place : taux × effectifs × haut du barème `cout_*_apu`, sans facteur PIB.
    - Hausse de x % du point : borne défavorable = barème haut avec retour 0,25 ; borne favorable = barème bas avec
      retour 0,32. L'effet croisé avec une indexation promise va dans la ligne de la hausse.
    - CSG déductible : retour d'impôt sur le revenu de 0,12 au central (0,10 à 0,15) ; aucun sur la CSG du capital.
    - Cotisation vieillesse de type non précisé : central du barème, sans retour.
    - APD : départ à `apd_part_rnb` sur `rnb_nominal_2032`, borne défavorable depuis 0,38 % (prévision 2026 citée par
      la presse spécialisée, source secondaire non inscrite dans `baremes.yaml`), borne favorable depuis 0,48 % (2024).
    - Retraites (âge) : les bornes n'incluent pas le coût toutes administrations.
    - Smic au-delà de 10 % : le produit linéaire est la borne favorable.
