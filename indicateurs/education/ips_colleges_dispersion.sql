-- Dispersion de l'IPS entre collèges : écart-type (échantillon) des IPS des collèges, non pondéré.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
ips AS (
    SELECT i.rentree_scolaire AS periode, i.ips, g.DEP
    FROM {{source:depp-ips-colleges}} AS i
    JOIN geo AS g ON i.code_insee_de_la_commune = g.COM
    WHERE i.ips IS NOT NULL
)
SELECT 'departement' AS maille, i.DEP AS code, d.LIBELLE AS libelle, i.periode,
       round(stddev_samp(i.ips), 1) AS valeur
FROM ips AS i JOIN {{source:insee-cog-departements}} AS d ON i.DEP = d.DEP
GROUP BY i.DEP, d.LIBELLE, i.periode
HAVING count(*) >= 2
UNION ALL
SELECT 'france', 'FR', 'France (hors COM)', periode, round(stddev_samp(ips), 1)
FROM ips
GROUP BY periode
