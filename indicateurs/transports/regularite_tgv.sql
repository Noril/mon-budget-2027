-- Régularité composite des TGV, moyenne simple des douze mois de l'année, en % (SNCF Voyageurs).
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, CAST(year(date) AS VARCHAR) AS periode,
       round(avg(regularite_composite), 2) AS valeur
FROM {{source:sncf-regularite-tgv}}
WHERE regularite_composite IS NOT NULL
GROUP BY year(date)
HAVING count(DISTINCT month(date)) = 12
