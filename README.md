# Programme 2027, en open data

Un programme pour la France et l'Europe, écrit entièrement en public : chaque constat et chaque proposition est une fiche Markdown, et chaque chiffre remonte jusqu'au fichier brut de son producteur.

Document de pilotage (plan, architecture, inventaire des données, pistes) : https://claude.ai/artifact/DKrPrnSnpCqQpHEaTrxk5i

## La chaîne

```
catalogue.yaml ─► pipelines.ingest ─► data/brut/<source>/<horodatage>/  (fichier d'origine + manifeste sha256)
                                  └─► data/normalise/<source>.parquet   (contrôles : colonnes, volumétrie, fraîcheur)
indicateurs/*.yaml + *.sql ─► pipelines.indicateurs ─► data/indicateurs/<id>@<version>.parquet + lignage.json
domaines/**/*.md ─► outils.construire ─► build/site/  (chaque {{ind:…}} remplacé par sa valeur et une note de lignage)
```

Un chiffre n'est jamais tapé dans une fiche : il est appelé.

```markdown
En 2025, {{ind:sante.ald_sans_mt@1.0.0 | france | 2025}} des patients en ALD n'ont pas de médecin traitant.
```

## Démarrer

```bash
uv sync
uv run python -m outils.valider          # schémas, catalogue, fiches, liens
uv run python -m pipelines.ingest        # sources actives du catalogue
uv run python -m pipelines.indicateurs
uv run python -m outils.construire       # écrit build/site/
uv run pytest
```

## Arborescence

```
VISION.md              le cap (P0, écrit par un humain)
axes/                  axes transverses
domaines/<domaine>/    README.md, diagnostic/*.md, propositions/*.md
europe/                compétences UE
indicateurs/           catalogue.yaml des sources, définitions YAML + SQL des indicateurs
pipelines/             ingestion et calcul (données hors git, dans data/)
outils/                validation et construction du site
schemas/               JSON Schema des sources, indicateurs, fiches
sources/               fiches de lecture du corpus d'évaluation
decisions/             journal des arbitrages
```

## Licences

Textes sous CC BY 4.0, code sous MIT (voir `LICENSE`), données sous leur licence d'origine, indiquée dans le catalogue. Les tables dérivées de sources sous ODbL (ameli, URSSAF) sont republiées sous ODbL.
