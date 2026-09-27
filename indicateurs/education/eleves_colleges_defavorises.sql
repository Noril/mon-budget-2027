-- Part des collégiens scolarisés dans un collège du quart le plus défavorisé (IPS sous le premier quartile
-- national des collèges de la même rentrée, calculé sur les collèges rattachés au COG).
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
colleges AS (
    SELECT i.rentree_scolaire AS periode, i.uai, i.ips, g.DEP
    FROM {{source:depp-ips-colleges}} AS i
    JOIN geo AS g ON i.code_insee_de_la_commune = g.COM
    WHERE i.ips IS NOT NULL
),
seuils AS (SELECT periode, quantile_cont(ips, 0.25) AS q1 FROM colleges GROUP BY periode),
ips AS (
    SELECT c.periode, c.DEP, e.nombre_eleves_total AS eleves, c.ips < s.q1 AS defavorise
    FROM colleges AS c
    JOIN seuils AS s USING (periode)
    JOIN {{source:depp-effectifs-colleges}} AS e
      ON e.numero_college = c.uai AND CAST(year(e.rentree_scolaire) AS VARCHAR) = left(c.periode, 4)
    WHERE e.nombre_eleves_total > 0
)
SELECT 'departement' AS maille, i.DEP AS code, d.LIBELLE AS libelle, i.periode,
       round(100 * coalesce(sum(i.eleves) FILTER (WHERE i.defavorise), 0) / sum(i.eleves), 1) AS valeur
FROM ips AS i JOIN {{source:insee-cog-departements}} AS d ON i.DEP = d.DEP
GROUP BY i.DEP, d.LIBELLE, i.periode
UNION ALL
SELECT 'france', 'FR', 'France (hors COM)', periode,
       round(100 * sum(eleves) FILTER (WHERE defavorise) / sum(eleves), 1)
FROM ips
GROUP BY periode
