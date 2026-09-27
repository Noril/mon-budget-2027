-- IPS moyen des collèges, pondéré par le nombre d'élèves du collège à la même rentrée.
-- Rattachement commune -> département par le COG (COMD et COMA via COMPARENT, comme apl_mg.sql) :
-- les collèges des collectivités d'outre-mer, absentes du COG, sortent du champ.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
ips AS (
    SELECT i.rentree_scolaire AS periode, i.ips, g.DEP, e.nombre_eleves_total AS eleves
    FROM {{source:depp-ips-colleges}} AS i
    JOIN geo AS g ON i.code_insee_de_la_commune = g.COM
    JOIN {{source:depp-effectifs-colleges}} AS e
      ON e.numero_college = i.uai AND CAST(year(e.rentree_scolaire) AS VARCHAR) = left(i.rentree_scolaire, 4)
    WHERE i.ips IS NOT NULL AND e.nombre_eleves_total > 0
)
SELECT 'departement' AS maille, i.DEP AS code, d.LIBELLE AS libelle, i.periode,
       round(sum(i.ips * i.eleves) / sum(i.eleves), 1) AS valeur
FROM ips AS i JOIN {{source:insee-cog-departements}} AS d ON i.DEP = d.DEP
GROUP BY i.DEP, d.LIBELLE, i.periode
UNION ALL
SELECT 'france', 'FR', 'France (hors COM)', periode, round(sum(ips * eleves) / sum(eleves), 1)
FROM ips
GROUP BY periode
