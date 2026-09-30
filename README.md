# Mon budget 2027

Les programmes de la présidentielle 2027 chiffrés en open data, et un jeu pour composer votre propre budget.

Chiffrage indépendant et rejouable des programmes des candidats à l'élection présidentielle de 2027. Chaque mesure
est citée mot pour mot avec son lien et son coût se recalcule à partir de barèmes publics communs. Un second modèle d'IA
vérifie le chiffrage, puis l'effet cumulé est projeté sur la dette publique jusqu'en 2032.

**Le site** (rapport, simulateur budgétaire, jeu du budget) est déployé sur Vercel à chaque mise à jour de `main`. Son
adresse figure dans la description du dépôt. Tout le site se génère depuis ce dépôt.

**Périmètre.** Huit candidats ou candidats pressentis (voir `chiffrage/programmes/`), droit de référence voté au
29 septembre 2026. Les programmes ne sont pas tous arrêtés : chaque fichier dit d'où viennent les mesures et
leur niveau de précision. Le chiffrage donne des ordres de grandeur comparables, pas une prévision. Les limites sont détaillées
dans `chiffrage/README.md` et sur la page « Méthode et limites » du site.

## Produit avec l'IA

La collecte des programmes, le chiffrage, sa vérification, les textes du site et le code sont produits avec des modèles
d'intelligence artificielle (Claude, d'Anthropic), sous la direction d'une personne qui a fixé la méthode et les règles.
Les garde-fous sont automatiques et publics (citations comparées à leur source, formules rejouables, barèmes sourcés,
recalcul indépendant des indicateurs), mais aucun économiste n'a encore relu les chiffrages (voir `AUDIT.md`).

## Rejouer

```bash
uv sync
uv run python -m pipelines.ingest        # sources ouvertes du catalogue (INSEE, Eurostat, FMI…)
uv run python -m pipelines.indicateurs   # indicateurs, dont les finances publiques de départ
uv run python -m outils.chiffrage        # build/chiffrage.html (rapport autonome), build/chiffrage.md, data/chiffrage.json
uv run python -m outils.simulateur       # build/simulateur.html : composer son propre budget et se situer
uv run python -m outils.jeu               # build/jeu.html : le jeu du budget
uv run python -m outils.site                # build/site/ : le site complet
uv run python -m outils.valider && uv run pytest
```

Prérequis : [uv](https://docs.astral.sh/uv/) et Python 3.12 ou plus.

## Arborescence

```
chiffrage/             méthode (README.md), droit de référence et conventions (REFERENCE.md),
                       barèmes communs (baremes.yaml), un fichier par programme (programmes/*.yaml)
plan/                  trajectoire de la dette : hypothèses sourcées (FMI), modèle, référence
catalogue/             sources de données ouvertes, un fichier YAML par domaine
indicateurs/           définitions YAML + SQL des indicateurs, recalculés indépendamment (verifications/)
pipelines/             ingestion (zone brute horodatée, zone normalisée contrôlée) et calcul des indicateurs
outils/                validation, chiffrage, simulateur, jeu, tableau de bord, recalcul, site public
site/                  informations d'édition du site (mentions légales)
schemas/               JSON Schema des sources, indicateurs, programmes et barèmes
```

## Principes

- **Même méthode pour tous** : même droit de référence (voté au 29 septembre 2026), mêmes barèmes, mêmes conventions
  (`chiffrage/REFERENCE.md`). Deux programmes qui promettent la même chose coûtent la même chose.
- **Tout se vérifie** : chaque mesure est citée mot pour mot, chaque formule peut être rejouée et chaque paramètre a sa
  source. Quand une mesure ne se chiffre pas, c'est écrit, avec son sens probable, et la note de précision en tient compte.
- **Aucun effet de second tour** dans le solde : la croissance, l'emploi et les taux invoqués par les candidats sont
  décrits, pas comptés.
- **Neutralité** : le chiffrage ne juge pas l'opportunité des mesures.

## Contribuer et corriger

Une erreur, une citation inexacte, un lien mort, un barème contestable : ouvrez une
[issue](https://github.com/Noril/mon-budget-2027/issues/new/choose) (gabarit « Erreur factuelle »). Les candidats et leurs
équipes peuvent demander une correction de la même façon. Voir `CONTRIBUTING.md` et `CODE_OF_CONDUCT.md`.

## Licences

Code sous MIT (`LICENSE`), textes et chiffrages sous CC BY 4.0, données sous leur licence d'origine, indiquée dans le
catalogue. Le détail est dans `LICENSES.md`. Pour citer le projet : `CITATION.cff`.
