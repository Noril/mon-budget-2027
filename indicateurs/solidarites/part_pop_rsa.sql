-- Part de la population couverte par le RSA (personnes des foyers allocataires CAF en décembre / population municipale 2023).
-- Les lignes multiples d'un même mois et département sont additionnées. France = départements ayant une population de référence.
WITH caf AS (
    SELECT CAST(year(dtreffre) AS VARCHAR) AS periode, numdep, sum(indnbp_rsa) AS couverts
    FROM {{source:caf-allocataires-departement}}
    WHERE month(dtreffre) = 12
    GROUP BY ALL
),
pop AS (
    SELECT GEO AS dep, CAST(OBS_VALUE AS DOUBLE) AS population
    FROM {{source:insee-populations-reference}}
    WHERE GEO_OBJECT = 'DEP' AND POPREF_MEASURE = 'PMUN'
),
j AS (
    SELECT c.periode, c.numdep, c.couverts, p.population
    FROM caf AS c JOIN pop AS p ON c.numdep = p.dep
    WHERE c.couverts IS NOT NULL
)
SELECT 'departement' AS maille, j.numdep AS code, d.LIBELLE AS libelle, j.periode,
       round(100 * j.couverts / j.population, 2) AS valeur
FROM j JOIN {{source:insee-cog-departements}} AS d ON j.numdep = d.DEP
UNION ALL
SELECT 'france', 'FR', 'France hors Mayotte', periode, round(100 * sum(couverts) / sum(population), 2)
FROM j
GROUP BY periode
