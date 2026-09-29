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

## Points ouverts
- Licences non ouvertes : `otan-depenses-defense` (non commercial), `top500-listes`, `fmi-weo`,
  `pe-participation-europeennes` (conditions propres au producteur).
- `insee-comptes-apu` : séries consolidées reprenant des montants non consolidés depuis 2023 ; le SQL de
  `finances.depenses_publiques` est à adapter.
- Barèmes ou paramètres incohérents entre montants 2026 et projection 2032 : `ir_baisse_1pct`, `hs_*`, simulateur
  `baisse-10-pct`, `csg`, `baisse-salaires`. `apd_part_rnb` (0,42 % contre 0,38 %), `cnracl_taux_employeur`, calendrier
  CVAE (LFI 2025 ou 2026) à trancher.
- Sources secondaires à remplacer par les sources primaires : `retailleau-lr` (AME, APD, justice des mineurs ; 80 Md€
  d'économies), trois mesures d'Attal issues du comparateur IFRAP.
- Dates de source : certaines portent la date de collecte, pas de publication.
- Environ 60 paramètres hors barèmes communs listés dans `chiffrage/besoins/`.
- Contraste du texte blanc sur les pastilles jaune et turquoise des candidats.
- `fraicheur_max_jours` vide pour environ 80 sources.
