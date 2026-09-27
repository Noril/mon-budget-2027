-- APL communal (Paris, Lyon, Marseille : par arrondissement), agrégé par moyenne pondérée par la population standardisée.
-- Rattachement commune -> département, région : COM et ARM portent DEP et REG ; les communes déléguées
-- ou associées (COMD, COMA), fusionnées depuis le millésime APL, les héritent de leur commune parente.
-- Un code présent à la fois en COM et en COMD (chef-lieu d'une commune nouvelle) prend la ligne COM.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP, coalesce(c.REG, p.REG) AS REG
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
apl AS (
    SELECT a.annee, a.code_commune, a.commune, a.apl, a.pop_standardisee, g.DEP, g.REG
    FROM {{source:drees-apl}} AS a
    LEFT JOIN geo AS g ON a.code_commune = g.COM
    WHERE a.apl IS NOT NULL
)
SELECT 'commune' AS maille, code_commune AS code, commune AS libelle, annee AS periode, apl AS valeur
FROM apl
UNION ALL
SELECT 'departement', a.DEP, d.LIBELLE, a.annee,
       round(sum(a.apl * a.pop_standardisee) / sum(a.pop_standardisee), 3)
FROM apl AS a JOIN {{source:insee-cog-departements}} AS d ON a.DEP = d.DEP
GROUP BY a.DEP, d.LIBELLE, a.annee
UNION ALL
SELECT 'region', a.REG, r.LIBELLE, a.annee,
       round(sum(a.apl * a.pop_standardisee) / sum(a.pop_standardisee), 3)
FROM apl AS a JOIN {{source:insee-cog-regions}} AS r ON a.REG = r.REG
GROUP BY a.REG, r.LIBELLE, a.annee
UNION ALL
SELECT 'france', 'FR', 'France hors Mayotte', annee,
       round(sum(apl * pop_standardisee) / sum(pop_standardisee), 3)
FROM apl
GROUP BY annee
