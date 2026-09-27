-- Densité carcérale = détenus / places opérationnelles, France entière, au 1er du mois (Tab6).
WITH t AS (
    SELECT date,
           max(CASE WHEN mesure = 'detenus' THEN valeur END) AS detenus,
           max(CASE WHEN mesure = 'capacite_operationnelle' THEN valeur END) AS places
    FROM {{source:justice-ecroues-mensuel}}
    WHERE tableau = 'Tab6' AND niveau = 'Total France entière'
    GROUP BY date
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, substr(date, 1, 7) AS periode,
       round(100 * detenus / places, 1) AS valeur
FROM t
WHERE detenus IS NOT NULL AND places > 0
