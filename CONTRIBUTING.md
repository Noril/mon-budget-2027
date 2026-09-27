# Contribuer

> Version provisoire, à relire par un juriste en P0.

- **Une PR = une fiche**, avec son en-tête YAML complet (`schemas/fiche.schema.json`) et ses sources. Sans source, elle reste en discussion.
- **Aucun chiffre tapé à la main** : appeler un indicateur, `{{ind:<id>@<version> | <maille>=<code> | <période>}}`. S'il n'existe pas, proposer d'abord sa définition dans `indicateurs/`.
- **Les faits se corrigent, les choix se débattent.** Une erreur chiffrée se corrige par PR ; un désaccord de fond ouvre une discussion rattachée à la fiche.
- **Affiliations déclarées** pour toute contribution substantielle (parti, entreprise, lobby).
- Avant d'ouvrir la PR : `uv run python -m outils.valider && uv run pytest`.
