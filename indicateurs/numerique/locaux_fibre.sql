-- Part des locaux raccordables à la fibre jusqu'à l'abonné (FttH), par trimestre (ARCEP, fichier communes).
-- Rattachement commune -> département, région par le COG, comme dans indicateurs/sante/apl_mg.sql :
-- COM et ARM portent DEP et REG ; COMD et COMA les héritent de leur commune parente ; un code en COM et COMD prend la ligne COM.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP, coalesce(c.REG, p.REG) AS REG
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
a AS (
    SELECT t.trimestre, t.locaux, t.ftth, g.DEP, g.REG
    FROM {{source:arcep-thd-deploiements-communes}} AS t
    LEFT JOIN geo AS g ON t.code_commune = g.COM
    WHERE t.locaux IS NOT NULL AND t.ftth IS NOT NULL
)
SELECT 'departement' AS maille, a.DEP AS code, d.LIBELLE AS libelle, a.trimestre AS periode,
       round(100 * sum(a.ftth) / sum(a.locaux), 1) AS valeur
FROM a JOIN {{source:insee-cog-departements}} AS d ON a.DEP = d.DEP
GROUP BY a.DEP, d.LIBELLE, a.trimestre
UNION ALL
SELECT 'region', a.REG, r.LIBELLE, a.trimestre, round(100 * sum(a.ftth) / sum(a.locaux), 1)
FROM a JOIN {{source:insee-cog-regions}} AS r ON a.REG = r.REG
GROUP BY a.REG, r.LIBELLE, a.trimestre
UNION ALL
SELECT 'france', 'FR', 'France', trimestre, round(100 * sum(ftth) / sum(locaux), 1)
FROM a
GROUP BY trimestre
