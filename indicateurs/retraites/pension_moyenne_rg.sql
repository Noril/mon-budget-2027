-- Montant mensuel moyen de la retraite de base de droit direct servie par le régime général au 31 décembre (CNAV).
SELECT 'france' AS maille, 'FR' AS code, 'France (régime général)' AS libelle,
       CAST(year(annees_normees) AS VARCHAR) AS periode,
       CAST(montant_mensuel_moyen_de_la_retraite_globale_en_euros AS DOUBLE) AS valeur
FROM {{source:cnav-pension-moyenne}}
WHERE categorie = 'Droit propre'
  AND montant_mensuel_moyen_de_la_retraite_globale_en_euros IS NOT NULL
