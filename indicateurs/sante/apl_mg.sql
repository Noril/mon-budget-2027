-- APL communal (Paris, Lyon, Marseille : par arrondissement), agrégé par moyenne pondérée par la population standardisée.
WITH apl AS (
    SELECT a.annee, a.code_commune, a.commune, a.apl, a.pop_standardisee, g.DEP, g.REG
    FROM {{source:drees-apl}} AS a
    LEFT JOIN (
        SELECT COM, DEP, REG FROM {{source:insee-cog-communes}} WHERE TYPECOM IN ('COM', 'ARM')
    ) AS g ON a.code_commune = g.COM
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
