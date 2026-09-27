-- Évolution sur cinq ans (%) des effectifs salariés privés au 31 décembre des activités informatiques et services d'information (NAF 62 et 63), URSSAF.
-- Rattachement commune -> département, région par le COG, comme dans indicateurs/sante/apl_mg.sql.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP, coalesce(c.REG, p.REG) AS REG
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
long AS (
    UNPIVOT (SELECT code_commune, code_ape, COLUMNS('^effectifs_salaries_\d{4}$') FROM {{source:urssaf-effectifs-informatique}})
    ON COLUMNS('^effectifs_salaries_\d{4}$') INTO NAME colonne VALUE effectifs
),
u AS (
    SELECT right(l.colonne, 4) AS annee, l.effectifs, g.DEP, g.REG
    FROM long AS l LEFT JOIN geo AS g ON l.code_commune = g.COM
    WHERE left(l.code_ape, 2) IN ('62', '63')
),
niveaux AS (
    SELECT 'departement' AS maille, u.DEP AS code, d.LIBELLE AS libelle, CAST(u.annee AS INTEGER) AS annee, sum(u.effectifs) AS effectifs
    FROM u JOIN {{source:insee-cog-departements}} AS d ON u.DEP = d.DEP
    GROUP BY u.DEP, d.LIBELLE, u.annee
    UNION ALL
    SELECT 'region', u.REG, r.LIBELLE, CAST(u.annee AS INTEGER), sum(u.effectifs)
    FROM u JOIN {{source:insee-cog-regions}} AS r ON u.REG = r.REG
    GROUP BY u.REG, r.LIBELLE, u.annee
    UNION ALL
    SELECT 'france', 'FR', 'France', CAST(annee AS INTEGER), sum(effectifs)
    FROM u
    GROUP BY annee
)
SELECT n.maille, n.code, n.libelle, CAST(n.annee AS VARCHAR) AS periode,
       round(100 * (n.effectifs / a.effectifs - 1), 1) AS valeur
FROM niveaux AS n
JOIN niveaux AS a ON a.maille = n.maille AND a.code = n.code AND a.annee = n.annee - 5
WHERE a.effectifs > 0
