# Besoins de barèmes : Marine Le Pen (RN)

Coûts unitaires à inscrire dans `chiffrage/baremes.yaml` pour chiffrer `programmes/le-pen-rn.yaml` (phase 2).
Montants en Md€ par an, régime 2032 sauf mention. Entre parenthèses : mesures concernées.

## Référence législative (à fixer avant tout chiffrage)

- Contenu adopté de la LFI 2026 et de la LFSS 2026 : barème de l'IR indexé ou gelé, « année blanche » des pensions et
  prestations, abattement retraités, taxe petits colis, taxe sur les mutuelles, taxe sur les avantages sociaux, LODEOM,
  apprentis, JEI, ACRE, Dutreil, super-IS, baisse des crédits agriculture (annulations-mesures-fiscales-budget-2026,
  indexation-bareme-ir-csg, indexation-pensions-prestations, hausses-credits-ciblees).
- Retraites : état de la réforme 2023 au 1er janvier 2027 (suspension LFSS 2026 jusqu'au 1er janvier 2028, puis
  calendrier de reprise vers 64 ans / 43 annuités) (retraites-60-62-ans).
- Calendrier légal d'extinction de la CVAE (suppression-cvae).

## TVA et fiscalité indirecte

- Coût d'une baisse de TVA de 20 % à 5,5 % par produit énergétique : carburants, électricité (consommation), gaz
  (consommation), fioul domestique, bois ; assiettes TTC hors TVA 2032 (tva-energie-5-5).
- Coût d'un point de TVA au taux normal / assiette des produits de première nécessité (alimentation, hygiène) au taux
  réduit (tva-100-produits-premiere-necessite).
- Rendement de l'octroi de mer (fiscalite-entreprises-divers).

## Impôt sur le revenu et patrimoine

- Coût du relèvement du quotient familial : part entière dès le 2e enfant (ir-part-pleine-deuxieme-enfant).
- Coût de la demi-part des veufs généralisée (ir-demi-part-veufs).
- Coût d'un point d'indexation du barème de l'IR (indexation-bareme-ir-csg).
- Rendement de l'IFI et de la taxe sur les holdings ; assiette du patrimoine financier des ménages au-delà de 1,3 M€
  (impot-fortune-financiere).
- Coût du raccourcissement à 15 ans de la durée d'exonération des plus-values immobilières (IR 19 % + PS 17,2 %)
  (plus-values-immobilieres-15-ans).

## Retraites et cotisations

- Coût d'un an d'âge légal de départ (et d'une annuité de durée requise) en 2032 ; coût d'un dispositif carrières
  longues à 60 ans avec 40 annuités pour les débuts avant 20 ans (retraites-60-62-ans).
- Effectifs en cumul emploi-retraite et au-delà de l'âge du taux plein ; taux de cotisation vieillesse et chômage
  (salarié, employeur) (cumul-emploi-retraite-sans-cotisations).
- Masse salariale jusqu'à 3 SMIC, taux de cotisations patronales effectif après allègements ; taux de recours à une
  hausse de 10 % (hausse-salaires-10-exoneree).
- Coût d'un point de revalorisation des pensions et des prestations (indexation-pensions-prestations).

## Impôts de production

- Rendement de la CFE, de la C3S, de la CVAE résiduelle en 2032 ; retour d'IS mécanique (déductibilité) (suppression-cfe,
  suppression-c3s, suppression-cvae).

## Prestations et immigration

- Dépense de RSA, prime d'activité, allocations familiales, APL, ASPA versée à des étrangers, et part des étrangers
  ayant moins de 5 ans d'emploi en France (prestations-solidarite-5-ans-travail).
- Dépense d'AME et coût des soins urgents résiduels (ame-en-amu).
- Nombre de visas pour soins et coût associé (suppression-visa-soins).
- Nombre d'étrangers chômeurs depuis plus d'un an sans ressources, allocations versées, coût unitaire d'un
  éloignement (chomeurs-etrangers-renvoi, fin-accord-franco-algerien-1968).
- Effectifs d'étudiants extra-communautaires, frais différenciés appliqués (frais-scolarite-etudiants-etrangers).
- Nombre de visas touristiques délivrés (timbre-visas-touristiques).

## Dépenses de l'État et des opérateurs

- Contribution française au budget de l'UE (PSR-UE) 2027-2032 (baisse-contribution-ue).
- Subventions pour charges de service public des opérateurs et taxes affectées (agences-operateurs-moins-20).
- Charges de soutien aux EnR électriques (CSPE budgétaire) selon le prix de marché, part des contrats en cours
  (fin-soutien-enr-intermittentes).
- Crédits MaPrimeRénov' ; coût budgétaire d'un PTZ (bonification pour 1 € prêté) (maprimerenov-en-pret-100-renov).
- Crédits de la mission APD (aide-publique-developpement), fonds vert (fonds-vert), aides à l'apprentissage par niveau
  de diplôme (aides-apprentissage-avant-licence).
- DGF des régions et des EPCI ; élasticité de la dépense locale à la dotation (dgf-regions-epci).
- Subventions aux associations (jaune budgétaire) (subventions-associations).
- Dotations des pouvoirs publics, audiovisuel public, aides à la presse, CESER (train-de-vie-etat-et-petites-economies).
- Économies attendues de la délivrance à l'unité et du contrôle des ALD (sante-medicaments-unite-ald).

## Recettes nouvelles

- Volume annuel des rachats d'actions des sociétés françaises (taxe-rachats-actions) ; volume des transactions
  intra-journalières (taxe-transactions-intrajournalieres) ; dividendes « exceptionnels » (taxe-superdividendes).
- Volume annuel des CEE (Md€) et dépenses qu'ils financent (rebudgetisation-cee).
- Rendement documenté des plans antifraude (lutte-contre-fraudes).

## Barèmes à ajouter (phase 2 : paramètres sourcés utilisés faute de barème)

- `cfe_rendement` : CFE 7,7 Md€ (2024, FIPECO « Les impôts sur la production ») ; `impots_production_entreprises` :
  86,8 Md€ (2024, même source).
- `is_retour_impots_production` : retour d'IS au taux moyen effectif de 20 % (Institut Montaigne, législatives 2024).
- `retraites_40_annuites_avant_20_ans` : coût du départ à 60 ans avec 40 annuités pour les carrières commencées avant 20
  ans (Institut Montaigne 2024 : 26,5 Md€ en 2027, hors abrogation 2023).
- `exoneration_hausse_salaires_10pct` : Institut Montaigne 2024 (0,8 / 4,8 / 12 Md€ les années 1, 3, 5 ; 15 Md€ bruts à terme).
- `quotient_familial_part_2e_enfant` : 3,4 Md€ (2024, LexImpact via Institut Montaigne).
- `tva_produits_premiere_necessite_0` : 4,7 à 8,8 Md€ (2023, Institut Montaigne).
- `preference_nationale_prestations` : Montaigne 2,5 (5 ans de travail) + 3,3 (prestations familiales) ; IFRAP 6 à 7 Md€.
- `cspe_enr_croissance_annuelle` : CRE, délibération 2026-149 (éolien + PV 6,25 → 7,29 Md€ de 2026 à 2027 ; soutien
  engagé jusqu'en 2029).
- Crédits PLF 2026 (Sénat) : Anah 1,5 ; mission APD 3,67 ; fonds vert 1,085 ; aide à l'embauche d'apprentis 2,37 ; mission
  Agriculture LFI 2026 4,126 (CP).
- Mesures votées en LFI/LFSS 2026 et leurs rendements : taxe petits colis 0,40 ; hausse TSBA 2025 ≈ 0,8 ; ACRE 0,184 ;
  ruptures conventionnelles 0,26 ; taxe holdings (≈ 0,9 au PLF, non chiffrée en LFI).
- Manquants (mesures laissées non chiffrables) : nombre et revenus des retraités en cumul emploi-retraite ; plus-values
  immobilières par durée de détention ; volume des rachats d'actions ; allocations chômage versées aux étrangers ; visas
  pour soins.
