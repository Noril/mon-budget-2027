# Le compte de la France

Brique financière du chiffrage : d'où part la France (solde, dette, intérêts), où la mène la politique actuelle
d'ici 2032, et ce que change chaque programme de candidat (`chiffrage/`).

```bash
uv run python -m pipelines.ingest insee-comptes-apu insee-pib eurostat-gov-10dd-edpt1 eurostat-gov-10a-main fmi-weo
uv run python -m pipelines.indicateurs
uv run python -m plan.trajectoire                                   # référence
uv run python -m plan.trajectoire --variante fmi                    # solde primaire des projections du FMI
uv run python -m plan.trajectoire --scenario plan/scenarios/exemple.yaml
```

Sorties : `data/plan/trajectoire_reference.parquet` (annee, croissance, inflation, taux, solde_primaire, solde,
dette, charge_interets, pib, nature) et son `.lignage.json` (empreinte des hypothèses, point de départ, fichiers
FMI, hypothèses à trancher) ; `data/plan/trajectoire_<scenario>.parquet` pour un scénario.

## Le modèle

Une seule équation, l'accumulation de la dette, en points de PIB :

```
g_nominale(t)      = (1 + croissance(t)) × (1 + inflation(t)) − 1
charge_interets(t) = taux(t) × dette(t−1) / (1 + g_nominale(t))
dette(t)           = dette(t−1) × (1 + taux(t)) / (1 + g_nominale(t)) − solde_primaire(t)
solde(t)           = solde_primaire(t) − charge_interets(t)
```

- **Point de départ** : dernière année observée commune à `finances.dette_publique`, `finances.solde_public`,
  `finances.charge_interets` et `finances.pib_nominal` (maille france). Le solde primaire de départ est
  solde + charge d'intérêts.
- **Hypothèses** : `plan/hypotheses.yaml`. Chaque valeur porte sa source (URL ouverte), sa date et sa
  `derivation` ; le programme recalcule chaque valeur depuis la source ingérée et s'arrête si elles divergent.
  Une hypothèse sans source publique porte `a_trancher: true` et une convention explicite.
- **Inflation** : c'est le déflateur du PIB (et non l'indice des prix à la consommation) qui fait passer du
  volume au nominal.
- **Taux** : taux apparent implicite des projections du FMI (intérêts nets / dette de l'année précédente).

## Ce que le modèle ne fait pas

- **Aucun effet en retour des réformes sur la croissance, l'inflation ou les taux.** Une mesure qui coûte
  10 Md€ dégrade le solde de 10 Md€, point. Les effets de second tour (multiplicateurs, recettes induites,
  prime de risque) ne sont pas modélisés : s'ils sont invoqués par un candidat, ils sont décrits et
  inscrits comme une ligne distincte du scénario, jamais noyés dans le coût.
- **Pas de modèle macroéconomique.** Croissance et inflation sont exogènes (FMI) ; le taux apparent ne réagit ni
  à la dette ni aux taux de marché ; il n'y a pas de structure de la dette par maturité.
- **Pas d'ajustements dette-déficit** (trésorerie, prêts, privatisations, primes et décotes à l'émission) :
  en pratique la dette observée s'écarte chaque année de quelques dixièmes de point de ce que donne l'équation.
- **Intérêts nets contre intérêts bruts** : le taux projeté vient des intérêts nets du FMI, la charge observée
  au départ est brute (Eurostat D41PAY). L'écart est de l'ordre de 0,1 à 0,2 point de PIB.
- **« Politique inchangée »** : aucune source publique ne donne de solde primaire à politique inchangée
  jusqu'en 2032. La référence gèle le solde primaire au dernier niveau observé (`a_trancher`). La variante `fmi`
  reprend le solde primaire du FMI, qui intègre le budget 2026 et un effort structurel minimal de 0,5 point par an :
  c'est une trajectoire de politique annoncée, pas inchangée. Le choix relève d'un arbitrage (`decisions/`).
- Les dernières années observées sont provisoires et révisées (INSEE fin mai et fin août, Eurostat avril et
  octobre).

## Sources et indicateurs

| Indicateur | Source | Remarque |
|---|---|---|
| `finances.solde_public` | INSEE Melodi `DD_CNA_APU` (B9) et `DD_CNA_AGREGATS` (PIB) ; Eurostat `gov_10dd_edpt1` (maille pays) | |
| `finances.dette_publique` | Eurostat `gov_10dd_edpt1` (GD / B1GQ) | Melodi n'a la dette de Maastricht que jusqu'en 1994 |
| `finances.charge_interets` | Eurostat `gov_10dd_edpt1` (D41PAY / B1GQ) | |
| `finances.taux_apparent` | Eurostat `gov_10dd_edpt1` (D41PAY(t) / GD(t−1)) | |
| `finances.depenses_publiques`, `finances.recettes_publiques` | Eurostat `gov_10a_main` (TE, TR en % du PIB) | séries consolidées Melodi fautives depuis 2023 |
| `finances.pib_nominal` | INSEE Melodi `DD_CNA_AGREGATS` | niveau de départ du PIB en Md€ |

Toutes les tables `finances.*` sauf le PIB ont une maille `pays` (codes Eurostat, dont `EU27_2020`) pour la
comparaison européenne : `{{ind:finances.dette_publique@1.0.0 | pays=DE | 2025}}`.

## Programmes des candidats

`outils/chiffrage.py` convertit les effets annuels de chaque programme (`chiffrage/programmes/*.yaml`) en points de
PIB et appelle `projeter` pour chacun, contre la référence gelée et la variante FMI (voir `chiffrage/README.md`).
Le format `--scenario` (`plan/scenarios/exemple.yaml`) reste disponible pour tester un jeu d'effets à la main.
