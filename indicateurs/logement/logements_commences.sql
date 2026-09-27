-- Logements commencés pour 1 000 habitants (Sitadel, séries départementales estimées en date réelle).
-- Années civiles complètes seulement ; population au 1er janvier de l'année (INSEE, estimations).
WITH s AS (
    SELECT DEPARTEMENT_CODE AS dep, CAST(ANNEE AS INTEGER) AS annee, MOIS, CAST(LOG_COM AS DOUBLE) AS logements
    FROM {{source:sdes-sitadel-departements}}
    WHERE TYPE_LGT = 'Tous Logements'
),
annees AS (SELECT annee FROM s GROUP BY annee HAVING count(DISTINCT MOIS) = 12),
par_dep AS (
    SELECT s.dep, s.annee, sum(s.logements) AS logements
    FROM s JOIN annees USING (annee)
    GROUP BY s.dep, s.annee
),
pop AS (
    SELECT GEO AS dep, CAST(TIME_PERIOD AS INTEGER) AS annee, CAST(OBS_VALUE AS DOUBLE) AS pop
    FROM {{source:insee-estimations-population}}
    WHERE GEO_OBJECT = 'DEP' AND EP_MEASURE = 'POP_JAN_1ST' AND AGE = '_T' AND SEX = '_T'
),
v AS (
    SELECT p.dep, d.LIBELLE AS libelle, p.annee, p.logements, pop.pop
    FROM par_dep AS p
    JOIN pop USING (dep, annee)
    JOIN {{source:insee-cog-departements}} AS d ON p.dep = d.DEP
)
SELECT 'departement' AS maille, dep AS code, libelle, CAST(annee AS VARCHAR) AS periode,
       round(1000 * logements / pop, 2) AS valeur
FROM v
UNION ALL
SELECT 'france', 'FR', 'France hors Mayotte', CAST(annee AS VARCHAR), round(1000 * sum(logements) / sum(pop), 2)
FROM v
GROUP BY annee
