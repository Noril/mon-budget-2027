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

## Vérifié en ligne le 30 septembre 2026
1. **Citations** (`uv run python -m outils.liens`) : les 453 citations écrites des 8 programmes sont retrouvées mot pour
   mot dans leur source (HTML ou PDF, après normalisation des espaces, apostrophes, césures et puces) ; les 2 citations
   orales (vidéos) ont été vérifiées par transcription (voir plus bas).
2. **Liens** (`--catalogue`) : 313 URL de barèmes et du catalogue testées ; 5 échecs, tous des 403 aux robots de liens
   valides (voir plus bas).
3. **Chaîne de données** : ingestion complète (une seule source injoignable depuis un robot, dernière version conservée),
   151 indicateurs calculés et recalculés indépendamment sans écart, trajectoire de référence, rapport, simulateur, jeu
   et site régénérés.

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

- **Curseurs du simulateur** : chaque position de candidat est désormais la somme de mesures nommées
  (`curseur.reprend`), recalculée par `--synchroniser` et contrôlée par la validation (LFI : santé 38,8, défense 22,8,
  éducation 33,8, transition 40,4) ; cartes du jeu ajustées pour que chaque programme reste rejouable à 1 Md€ près.
- **Attributions sans source primaire** retirées du simulateur (Attal, baisse d'impôt « classes moyennes » ; Retailleau,
  baisse de l'aide au développement) ; la validation refuse désormais d'attribuer une option à un candidat sur la foi
  d'une mesure non chiffrée.

- **Citations orales** (Zemmour) : verbatim établi par transcription automatique (Whisper large-v3-turbo) des extraits
  vidéo, les sous-titres YouTube étant fermés aux robots. `retraite-64-voire-65` : le titre BFMTV reformulait ; citation
  remplacée par « Je dis 64 voire 65. […] Je pense qu’il faut travailler plus » (Face à BFM, 0:46-0:54).
  `ia-nucleaire-priorite` : le titre YouTube (« L’IA est… ») reformulait ; citation remplacée par la phrase prononcée
  (« C’est la troisième grande révolution industrielle de l’histoire de l’Occident, après la machine à vapeur, après
  l’électricité »), transcrite depuis le même extrait publié par CNews sur X et recoupée par le compte rendu écrit de CNews.
- **`insee-comptes-apu`** : anomalie confirmée sur les données (OTE consolidé 1 550 Md€ en 2022, 2 138 Md€ en 2023 ;
  D41 consolidé = non consolidé dès 2023). `finances.depenses_publiques` et `recettes_publiques` lisaient déjà Eurostat
  (gov_10a_main, TE/TR, 2025 compris) : valeurs justes, inchangées. Seul `finances.solde_public` lit ce jeu (B9, invariant
  par consolidation) : garde-fou ajouté dans le SQL et dans `verifications/finances_solde_public.py` (échec si B9
  consolidé ≠ non consolidé) ; sortie inchangée, version 1.0.0 conservée ; 151 indicateurs recalculés sans écart.
- **Dates de source** : dates de collecte (2026-09-29, « 2026-09 ») remplacées par la date de publication quand la page ou
  le PDF la donne (3 : profession de foi Glucksmann, deux articles irdeme.org), par « mis à jour le … » pour les pages
  qui évoluent (`dateModified` : choisir2027.fr, LFI, republicains.fr, votons-2027 ×3), sinon écrites « consulté le
  2026-09-29 » (33 : comparateur IFRAP, budget2026.fr, combienjegagne.fr, Wikipédia, glucks2027.fr). `baremes.yaml` :
  aucune date de collecte.
- **Licences non ouvertes** (conditions lues le 30/09, citées dans `notes` du catalogue, `LICENSES.md` aligné) : aucune
  n'interdit de publier des tables dérivées ; publication maintenue avec mention de la source. OTAN : crédit obligatoire,
  ni vente ni publicité. FMI (conditions du 11/10/2024) : données réutilisables avec attribution, transformation signalée,
  usage commercial sur autorisation. Parlement européen (mentions légales d'elections.europa.eu) : réutilisation avec
  source et URL. TOP500 : aucune licence publiée ; seules des parts agrégées par pays sont publiées, jamais la liste.
  Le tableau de bord se termine désormais par une section « Sources et licences » ; les pages mentionnent le WEO du FMI
  comme données transformées.

## Points ouverts
- TOP500 : absence de licence ; la publication de parts agrégées repose sur une lecture des conditions (« create
  additional sublists and statistics »), pas sur une autorisation écrite ; à confirmer auprès de Prometeus GmbH.
- Dates : date de mise en ligne du plan Knafo (budget2026.fr) inconnue ; livret École LR laissé à « 2026-09 » (daté
  ainsi par le document).
- Environ 60 paramètres hors barèmes communs listés dans `chiffrage/besoins/`.
- Recette de la CVAE : 3,7 Md€ prélevés (FIPECO, 2025) contre 4,0 à 4,3 Md€ de recette budgétaire ; le rythme de
  recouvrement 2028-2029 et le PLF 2027 (non déposé) peuvent déplacer les coûts d'avance.
