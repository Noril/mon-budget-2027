# Chiffrer les programmes 2027, en open data

Chiffrage indépendant et rejouable des programmes des candidats à l'élection présidentielle de 2027 : chaque mesure
est citée verbatim avec son lien, son coût se recalcule à partir de barèmes publics communs, un second agent vérifie
le chiffrage, et l'effet cumulé est projeté sur la dette publique jusqu'en 2032.

```bash
uv sync
uv run python -m pipelines.ingest        # sources ouvertes du catalogue (INSEE, Eurostat, FMI…)
uv run python -m pipelines.indicateurs   # indicateurs, dont les finances publiques de départ
uv run python -m outils.chiffrage        # build/chiffrage.html (rapport autonome), build/chiffrage.md, data/chiffrage.json
uv run python -m outils.simulateur       # build/simulateur.html : composer son propre budget et se situer
uv run python -m outils.valider && uv run pytest
```

## Arborescence

```
chiffrage/             méthode (README.md), droit de référence et conventions (REFERENCE.md),
                       barèmes communs (baremes.yaml), un fichier par programme (programmes/*.yaml)
plan/                  trajectoire de la dette : hypothèses sourcées (FMI), modèle, référence
catalogue/             sources de données ouvertes, un fichier YAML par domaine
indicateurs/           définitions YAML + SQL des indicateurs, recalculés indépendamment (verifications/)
pipelines/             ingestion (zone brute horodatée, zone normalisée contrôlée) et calcul des indicateurs
outils/                validation, chiffrage, simulateur, tableau de bord, recalcul
schemas/               JSON Schema des sources, indicateurs, programmes et barèmes
```

## Principes

- **Même méthode pour tous** : même droit de référence (voté au 29 septembre 2026), mêmes barèmes, mêmes conventions
  (`chiffrage/REFERENCE.md`). Deux programmes qui promettent la même chose coûtent la même chose.
- **Rien d'invérifiable** : citation verbatim, formule rejouable, paramètres sourcés ; ce qui ne se chiffre pas est
  dit, avec son sens probable, et mesuré par une note de précision.
- **Aucun effet de second tour** dans le solde : la croissance, l'emploi et les taux invoqués par les candidats sont
  décrits, pas comptés.
- **Neutralité** : le chiffrage ne juge pas l'opportunité des mesures.

## Licences

Textes sous CC BY 4.0, code sous MIT (voir `LICENSE`), données sous leur licence d'origine, indiquée dans le catalogue.
