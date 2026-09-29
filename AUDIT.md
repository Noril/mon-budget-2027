# Audit avant publication (29 septembre 2026)

La partie « passe sources » (citations, barèmes, glossaire, recalage des programmes) est dans l'historique de `main`
(commits « Passe sources »). L'audit ci-dessous a été fait hors ligne, sans accès réseau sortant : il ne couvre que ce qui
n'a pas pu être rejoué en ligne. Les points marqués « non vérifié » sont à confirmer à la lumière de la passe sources.

## Contrôlé
- Arithmétique des 113 barèmes, des hypothèses et du modèle de dette recalculée ; une douzaine d'écarts corrigés
  (`git log -- chiffrage/baremes.yaml`).
- Glossaire (110 termes), cartes du jeu et simulateur relus et alignés sur les barèmes.
- Schémas, renvois aux barèmes, unicité des identifiants, citation et URL présentes pour chaque mesure : tests
  automatiques.
- Pages générées : échappement du contenu, autonomie (aucune ressource externe), accessibilité de base.
- Quelques chiffres recoupés par recherche (TVA, IS, COR, FMI avril 2026, PFU…), sans lecture des pages sources.

## Non vérifié : à faire avec un accès réseau
1. **Liens et citations** des 8 programmes : aucun lien n'a été ouvert, aucune citation verbatim n'a été comparée à sa
   source. À faire avant de promouvoir le site.
2. **Catalogue** : 109 sources, 215 URL non testées ; licences à confirmer sur les fiches des producteurs.
3. **Ingestion et indicateurs** : `pipelines.ingest` n'a pas tourné (403 partout), donc indicateurs, recalcul,
   trajectoire et pages générées n'ont pas été reconstruits.

## Réglé le 30 septembre 2026 (en ligne)
- **2026 contre 2032** : `ir_baisse_1pct` (le `haut` 1,26 mêlait une projection 2032, avec le facteur 2025→2032, à des
  montants 2025-2026 : retiré, projection en dérivation) ; `hs_exoneration_cout` (`bas` 5,2 = exécution 2024 retiré ;
  réaction à une suppression sourcée : −7,1 % d'heures supplémentaires, OFCE 2012) et `melenchon-lfi/heures-sup-fiscalisation`
  (bas 5,2 → 5,94) ; simulateur `impot-revenu/baisse-10-pct` (10,4 en euros 2026 → 12,3 en 2032) et
  `point-indice/hausse-3-pct` (effet brut 5,6 → net 4,0, comme le reste du levier) ; `csg/baisse-salaires`
  (Glucksmann : enveloppe de 15 Md€ projetée en 2032 au central, −12,6 → −14,9) ; même enveloppe côté Retailleau
  (`restitution-pouvoir-achat-salaries`, retour d'IR de la convention 5 appliqué : −17,8 → −14,9) ; aides du simulateur
  (CSG, IR, heures supplémentaires) datées 2026 et 2032.
- **`apd_part_rnb`** : 0,42 % en 2025 confirmé (OCDE, API DAC1) ; aucune prévision officielle 2026 (le DPT du PLF 2026
  s'arrête à 2025) ; le 0,38 % vient de Focus 2030 (projection d'ONG), inscrit en `bas` avec sa source ; les trois
  programmes qui promettent 0,7 % ont la même borne défavorable (Glucksmann : bas −11,06 → −11,79).
- **`cnracl_taux_employeur`** : 37,65 % en 2026, décret n° 2025-86 modifiant l'article 5 du décret n° 91-613 (Légifrance).
- **CVAE** : calendrier de la LFI 2025 (loi n° 2025-127, art. 62 : 0,28 % en 2026-2027, 0,19 % en 2028, 0,09 % en 2029,
  suppression en 2030), non modifié par la LFI 2026 (loi n° 2026-103) ; REFERENCE.md, `cvae_restante` (haut 4,04 Md€,
  état A 2026) et cinq programmes corrigés (« LFI 2026 » → « LFI 2025 »).
- **Sources secondaires** : `retailleau-lr/ame-reduction` a sa source primaire (entretien au Parisien reproduit sur
  republicains.fr) ; `aide-publique-developpement-baisse` passe en non chiffrable (seule trace : l'IFRAP ; estimation
  indicative 1,2) ; les « 80 Md€ » d'économies (source unique indirecte) sont écartés ; justice des mineurs déjà sourcée
  en primaire. Attal : sources primaires introuvables pour les trois apports IFRAP, notées dans `interpretation`,
  montants inchangés (mesures non chiffrables ou indicatives).
- **Montants de programmes écrits en dur** dans `cartes.yaml` et `simulateur.yaml` alignés sur les chiffrages actuels
  (santé 33, conscription 23, plan d'investissement 40, garantie d'autonomie 54, école 27,5, écarts cités dans `calcul`).
  Cartes : baisse de cotisations patronales confiée à l'économiste, zéro cotisation sur les heures supplémentaires à la
  patronne de PME.
- **Contraste** : couleurs des candidats et des personnages ≥ 4,5:1 avec le blanc (jaune #7d6608, turquoise #117864,
  orange #a04000, vert #196f3d) ; test `test_couleurs_contraste_aa`.
- **`fraicheur_max_jours`** renseigné pour 81 sources (annuel 400, semestriel 200, trimestriel 120, bimestriel 70,
  mensuel 45, quotidien 7, scrutins 1 900, enquêtes triennales 1 200) ; `sies-insertion-master` laissé vide (enquête
  arrêtée à la promotion 2020).
- **Liens** (`outils.liens --catalogue`) : `pe-participation-europeennes` (page déplacée), `ce-budget-ue-depenses-recettes`
  (fichier 2000-2023 retiré, remplacé par 2000-2025 ; la ligne des contributions nationales n'y figure plus pour 2021 et
  après : reconstituée dans les trois SQL, identique au centime près), `aspa_depense` et `aah_au_smic_cout` (copies
  Wayback de l'Institut Montaigne), `defense_*` (texte adopté n° 325 de l'Assemblée en seconde source). Restent 5 échecs,
  tous des 403 aux robots de liens valides pour un lecteur : Légifrance (4 : `cvae_restante`, `cnracl_taux_employeur` ×2,
  `defense_0_1_point_pib_2032`, chacun doublé d'une source accessible : BOFiP, CNRACL, Assemblée nationale) et
  imf.org (`fmi-weo`, page d'accueil du WEO, archivée en 200 le 6 juillet 2026 ; les données passent par api.imf.org).

## Points ouverts
- Licences non ouvertes : `otan-depenses-defense` (non commercial), `top500-listes`, `fmi-weo`,
  `pe-participation-europeennes` (conditions propres au producteur).
- `insee-comptes-apu` : séries consolidées reprenant des montants non consolidés depuis 2023 ; le SQL de
  `finances.depenses_publiques` est à adapter.
- Dates de source : certaines portent la date de collecte, pas de publication.
- Environ 60 paramètres hors barèmes communs listés dans `chiffrage/besoins/`.
- Positions des curseurs du simulateur (santé, défense, éducation, transition, recherche) : non recalculées par
  `--synchroniser` et en partie antérieures aux chiffrages actuels (LFI : santé 36,5, défense 27,3, éducation 35,8,
  transition 41,2) ; à reconstituer par un outil.
- `aide-developpement/reduction` associe encore Retailleau (mesure devenue non chiffrable) : option et candidats à
  revoir avec la synchronisation.
- Recette de la CVAE : 3,7 Md€ prélevés (FIPECO, 2025) contre 4,0 à 4,3 Md€ de recette budgétaire ; le rythme de
  recouvrement 2028-2029 et le PLF 2027 (non déposé) peuvent déplacer les coûts d'avance.
