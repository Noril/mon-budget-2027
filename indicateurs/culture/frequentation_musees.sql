-- Entrées dans les musées de France (payantes + gratuites), par année.
-- Département : commune du musée rattachée par le COG 2026 (COMD et COMA via leur commune parente) ;
-- à défaut, deux premiers caractères du code commune (trois en outre-mer).
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
m AS (
    SELECT f.annee, coalesce(g.DEP, CASE WHEN f.codeInseeCommune LIKE '97%' THEN left(f.codeInseeCommune, 3)
                                         ELSE left(f.codeInseeCommune, 2) END) AS dep,
           CAST(f.total AS BIGINT) AS entrees
    FROM {{source:culture-frequentation-musees}} AS f
    LEFT JOIN geo AS g ON f.codeInseeCommune = g.COM
    WHERE TRY_CAST(f.total AS BIGINT) IS NOT NULL
)
SELECT 'departement' AS maille, m.dep AS code, d.LIBELLE AS libelle, m.annee AS periode, CAST(sum(m.entrees) AS DOUBLE) AS valeur
FROM m JOIN {{source:insee-cog-departements}} AS d ON m.dep = d.DEP
GROUP BY m.dep, d.LIBELLE, m.annee
UNION ALL
SELECT 'france', 'FR', 'France', annee, CAST(sum(entrees) AS DOUBLE)
FROM m
GROUP BY annee
