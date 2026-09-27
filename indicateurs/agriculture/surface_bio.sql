-- Surface en agriculture biologique (certifiée et en conversion), hectares, Agence Bio, par département.
-- « NC » (secret statistique) compté comme absent. France = somme de toutes les lignes, Saint-Martin (978) compris.
WITH v AS (
    SELECT annee AS periode, codedepartement AS dep, TRY_CAST(surfbio AS DOUBLE) AS surface
    FROM {{source:agencebio-surfaces-departement}}
    WHERE TRY_CAST(surfbio AS DOUBLE) IS NOT NULL
)
SELECT 'departement' AS maille, v.dep AS code, d.LIBELLE AS libelle, v.periode, round(v.surface, 2) AS valeur
FROM v JOIN {{source:insee-cog-departements}} AS d ON v.dep = d.DEP
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(sum(surface), 2) FROM v GROUP BY periode
