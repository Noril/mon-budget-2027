# Santé

Domaine pilote (voir `decisions/0001-domaine-pilote.md`), sous l'angle de l'accès aux soins.

## Constats

- [[acces-generalistes]] — brouillon
- [[ald-sans-medecin-traitant]] — brouillon

## Indicateurs

| Indicateur | Source | Maille | Statut |
| --- | --- | --- | --- |
| `sante.ald_sans_mt` | ameli-ald-sans-mt | France, région, département | calculé |
| `sante.apl_mg` | drees-apl + COG | France, région, département, commune | calculé |
| `sante.pop_apl_mg_faible` | drees-apl + COG | France, région, département | calculé, seuil à valider |
| `sante.densite_mg_liberaux` | ameli-demographie-ps | France, région, département | calculé |

## Propositions

- [[equipes-soins-primaires-zones-sous-denses]] — brouillon, coût à chiffrer dans `plan/`

À instruire : régulation de l'installation des médecins (arbitrage séparé), budget global hospitalier, versement d'office des prestations (onglet « Pistes disruptives » du document de pilotage).

## Corpus d'évaluation

Dix fiches dans `sources/` sur l'accès aux soins primaires ; trous connus : régulation allemande, télémédecine, incitations nordiques et britanniques.
