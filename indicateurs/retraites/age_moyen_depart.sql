-- Âge moyen à l'attribution d'une retraite de droit direct au régime général (CNAV).
SELECT 'france' AS maille, 'FR' AS code, 'France (régime général)' AS libelle,
       CAST(year(annee) AS VARCHAR) AS periode,
       droits_directs AS valeur
FROM {{source:cnav-age-attribution}}
WHERE droits_directs IS NOT NULL
