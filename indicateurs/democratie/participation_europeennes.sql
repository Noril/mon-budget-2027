-- Participation aux élections européennes : votants / inscrits, en %.
-- France et départements : ministère de l'Intérieur. Pays : Parlement européen (taux publiés, 1979-2024) ;
-- agrégat UE (EU27_2020) seulement pour 2024, seule année où l'Union comptait ces 27 États.
WITH r AS (
    SELECT annee, code_departement, inscrits, votants
    FROM {{source:interieur-europeennes-departements}}
    WHERE scrutin = 'europeennes'
),
pe AS (
    SELECT CAST(YEAR AS INTEGER) AS annee, coalesce(COUNTRY_ID, 'EU27_2020') AS code, CAST(RATE AS DOUBLE) AS taux
    FROM {{source:pe-participation-europeennes}}
    WHERE COUNTRY_ID IS NOT NULL OR YEAR = '2024'
)
SELECT 'departement' AS maille, r.code_departement AS code, d.LIBELLE AS libelle, CAST(r.annee AS VARCHAR) AS periode,
       round(100 * r.votants / r.inscrits, 2) AS valeur
FROM r JOIN {{source:insee-cog-departements}} AS d ON r.code_departement = d.DEP
UNION ALL
SELECT 'france', 'FR', 'France (y compris Français de l''étranger)', CAST(annee AS VARCHAR),
       round(100 * sum(votants) / sum(inscrits), 2)
FROM r
GROUP BY annee
UNION ALL
SELECT 'pays', code, CASE WHEN code = 'EU27_2020' THEN 'Union européenne (27)' ELSE code END, CAST(annee AS VARCHAR), taux
FROM pe
