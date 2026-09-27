-- Part de la population totale (non standardisée) vivant sous le seuil d'APL de 2,5.
WITH apl AS (
    SELECT a.annee, a.apl, a.pop_totale, g.DEP, g.REG
    FROM {{source:drees-apl}} AS a
    LEFT JOIN (
        SELECT COM, DEP, REG FROM {{source:insee-cog-communes}} WHERE TYPECOM IN ('COM', 'ARM')
    ) AS g ON a.code_commune = g.COM
    WHERE a.apl IS NOT NULL
)
SELECT 'departement' AS maille, a.DEP AS code, d.LIBELLE AS libelle, a.annee AS periode,
       round(100 * coalesce(sum(a.pop_totale) FILTER (WHERE a.apl < 2.5), 0) / sum(a.pop_totale), 2) AS valeur
FROM apl AS a JOIN {{source:insee-cog-departements}} AS d ON a.DEP = d.DEP
GROUP BY a.DEP, d.LIBELLE, a.annee
UNION ALL
SELECT 'region', a.REG, r.LIBELLE, a.annee,
       round(100 * coalesce(sum(a.pop_totale) FILTER (WHERE a.apl < 2.5), 0) / sum(a.pop_totale), 2)
FROM apl AS a JOIN {{source:insee-cog-regions}} AS r ON a.REG = r.REG
GROUP BY a.REG, r.LIBELLE, a.annee
UNION ALL
SELECT 'france', 'FR', 'France hors Mayotte', annee,
       round(100 * coalesce(sum(pop_totale) FILTER (WHERE apl < 2.5), 0) / sum(pop_totale), 2)
FROM apl
GROUP BY annee
