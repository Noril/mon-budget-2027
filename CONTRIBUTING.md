# Contribuer

Le projet chiffre les programmes de la présidentielle 2027 avec une seule méthode pour tous. Toute contribution qui
améliore l'exactitude, la traçabilité ou la couverture est la bienvenue, quelle que soit la sensibilité politique de
son auteur : **seules les sources comptent**.

## Signaler une erreur
Ouvrez une issue « Erreur factuelle » (citation inexacte, attribution erronée, lien mort, erreur de calcul). Joignez la
source qui le démontre. Les candidats et leurs équipes peuvent demander une correction de la même façon.

## Proposer une modification
1. `uv sync`, puis `uv run python -m outils.valider && uv run pytest -q` doivent passer avant et après.
2. **Une mesure** (`chiffrage/programmes/<id>.yaml`) : citation mot pour mot, URL, date, candidat ou proche attribué
   correctement, lecture retenue si la promesse est ambiguë (`interpretation`), niveau de précision.
3. **Un chiffre** : il vient d'un barème commun (`chiffrage/baremes.yaml`) avec ses sources et sa dérivation. Un barème
   contesté s'applique à tous les programmes, jamais à un seul. Pas d'effet de second tour dans le solde.
4. **Une donnée** : source ouverte dans `catalogue/` (licence indiquée), indicateur en YAML + SQL, recalculé
   indépendamment (`outils/recalcul`).
5. Une vérification indépendante (`verification`) est faite par quelqu'un d'autre que l'auteur de la mesure.
6. Pas de jugement sur l'opportunité d'une mesure dans les textes, les titres ou les libellés.

## Vérification
La CI valide les schémas, les renvois aux barèmes, les tests, puis rejoue toute la chaîne (ingestion, indicateurs,
recalcul, trajectoire, chiffrage). Les corrections sont conservées dans l'historique git, qui fait foi.

## Conduite
Voir [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
