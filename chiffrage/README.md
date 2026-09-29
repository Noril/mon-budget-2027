# Chiffrage des programmes 2027

Chiffrer les programmes des candidats avec la même méthode, les mêmes barèmes et la même trajectoire de dette,
chaque mesure citée verbatim et chaque montant rejouable.

```bash
uv run python -m outils.chiffrage --valider   # schémas, formules, renvois aux barèmes
uv run python -m outils.chiffrage             # build/chiffrage.md, build/chiffrage.html, data/chiffrage.json
```

## Fichiers

- `baremes.yaml` : coûts unitaires communs (schéma `schemas/bareme.schema.json`) : coût d'un point de TVA, d'un
  an d'âge légal de retraite, de 1 % de revalorisation des pensions, du point d'indice, etc. Chaque barème porte
  ses sources (URL ouvertes), sa dérivation et son millésime. Deux programmes qui promettent la même chose ont
  donc le même coût.
- `programmes/<id>.yaml` : un programme (schéma `schemas/programme.schema.json`) : sources, annonce globale du
  candidat telle quelle, et mesures.

## Règles de chiffrage

1. **Citation d'abord.** Une mesure n'entre que citée verbatim avec son URL (site du candidat ou du parti,
   programme, discours, entretien publié). Quand la promesse est ambiguë, `interpretation` dit la lecture retenue ;
   `precision` dit si la promesse est précise, partielle ou vague.
2. **Effet sur le solde public primaire**, toutes administrations publiques confondues (État, sécurité sociale,
   collectivités), en Md€ courants par an **en régime de croisière (2032)**, par rapport à la législation en
   vigueur au 1er janvier 2027. Négatif = coût (dépense nouvelle ou recette perdue).
3. **Effets comptés** : effets directs et mécaniques sur les comptes publics, y compris les retours certains à
   l'intérieur des administrations (cotisations et impôts payés sur une hausse de salaire public, par exemple) et,
   pour un impôt, la réaction de l'assiette documentée par une source publique (DG Trésor, CPO, Cour des comptes,
   IPP…). **Effets non comptés** : croissance, emploi, inflation, taux d'intérêt. Invoqués par le candidat, ils sont
   décrits dans `effets_retour`, jamais ajoutés au montant.
4. **Fourchette** : `bas` = hypothèse la plus défavorable au solde, `haut` = la plus favorable. Elle traduit
   l'incertitude sur les paramètres et sur la lecture de la promesse.
5. **Formule rejouable** : `calcul.formule` est une expression évaluée sur `calcul.parametres` ; elle doit redonner
   `central`. Un paramètre vient d'un barème (`bareme`, même valeur) ou porte sa `source`.
6. **Économies annoncées sans mesure détaillée.** Deux cas, traités de la même façon dans tous les programmes :
   - **Enveloppe globale** (« 100 Md€ d'économies », sans périmètre) : ce n'est pas une mesure. `central` = la
     part documentée par des mesures identifiables et chiffrées par ailleurs dans le programme (sans double compte,
     donc souvent 0), `haut` = montant annoncé, `bas` = 0. La différence est l'écart d'affichage.
   - **Économie ciblée sur un périmètre nommé** (« −20 % sur les agences », « 50 Md€ d'aides aux entreprises en
     moins ») : c'est une mesure, chiffrée comme si elle était appliquée, symétriquement aux dépenses promises.
     `central` = montant annoncé, **plafonné** par le budget réel du périmètre visé (source à l'appui) et par ce que
     le droit permet (une contribution à l'UE ne se baisse pas unilatéralement) ; `bas` = 0 (économie non
     réalisée) ; `haut` = `central`. Confiance faible sauf détail des postes.
6 bis. **Transferts entre administrations** (État → collectivités, sécurité sociale → État) : neutres sur le solde
   des APU, sauf la dépense nouvelle qu'ils financent. Un transfert fléché vers une dépense promise (« une fraction
   de TVA aux communes qui construisent ») compte comme cette dépense ; `haut` = 0 si la dépense n'est pas certaine.
7. **Non chiffrable** : réformes institutionnelles, mesures sans effet budgétaire significatif (< 0,1 Md€) ou trop
   vagues pour être lues. `raison_non_chiffrable` le dit, et `sens_probable` (coût, économie, neutre, incertain) dit
   dans quel sens la mesure pèserait. Pour une mesure trop vague mais dont l'objet est clair, `estimation_indicative`
   donne un ordre de grandeur (lecture la plus plausible, fourchette large, sources) : il est affiché à part et
   **n'entre pas dans le solde principal**. Le rapport montre ainsi la couverture de chaque programme et le sens du
   biais qu'introduisent les mesures non chiffrées.
8. **Chiffrages tiers** : Institut Montaigne, IFRAP, OFCE, IPP, Terra Nova, Cour des comptes, COR, presse
   spécialisée. Consignés avec leur montant et leur lien ; un écart important avec notre chiffre est expliqué.
9. **Vérification indépendante** : un second agent, qui n'a pas écrit le chiffrage, relit la citation, rejoue la
   formule, contrôle les paramètres dans les sources et renseigne `verification` (ok, corrige, conteste).

## Trajectoire de dette

Les effets annuels (régime de croisière × montée en charge) sont convertis en points de PIB et injectés dans
`plan/trajectoire.py`, contre deux références : solde primaire gelé au dernier niveau observé, et solde primaire
des projections du FMI. Le modèle n'a aucun effet en retour (voir `plan/README.md`) : il montre l'arithmétique
des promesses, pas leur effet macroéconomique.

## Limites

- Les programmes évoluent jusqu'au dépôt des candidatures : chaque fichier porte sa date de collecte.
- Un programme non encore publié en entier est chiffré sur ses mesures connues ; le nombre de mesures non
  chiffrables est affiché à côté du solde.
- Le chiffrage ne juge pas l'opportunité des mesures ; il en donne le coût.
