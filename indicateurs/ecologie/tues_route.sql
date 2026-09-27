-- Personnes tuées sur les routes par million d'habitants.
-- Départements et France : ONISR (BAAC) et population INSEE au 1er janvier. Pays : Eurostat (nombre / population moyenne).
WITH pop AS (
    SELECT GEO AS dep, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS pop
    FROM {{source:insee-estimations-population}}
    WHERE GEO_OBJECT = 'DEP' AND EP_MEASURE = 'POP_JAN_1ST' AND AGE = '_T' AND SEX = '_T'
),
dep AS (
    SELECT o.dep, d.LIBELLE AS libelle, o.annee AS periode, sum(o.tues) AS tues, any_value(pop.pop) AS pop
    FROM {{source:onisr-baac}} AS o
    JOIN {{source:insee-cog-departements}} AS d ON o.dep = d.DEP
    JOIN pop ON pop.dep = o.dep AND pop.periode = o.annee
    GROUP BY o.dep, d.LIBELLE, o.annee
),
eu AS (
    SELECT split_part(r.geo, ':', 1) AS code, substr(r.geo, strpos(r.geo, ':') + 1) AS libelle, r.TIME_PERIOD AS periode,
           CAST(r.OBS_VALUE AS DOUBLE) AS tues
    FROM {{source:eurostat-tran-sf-roadus}} AS r
    WHERE split_part(r.unit, ':', 1) = 'NR' AND split_part(r.sex, ':', 1) = 'T' AND split_part(r.age, ':', 1) = 'TOTAL'
      AND split_part(r.pers_cat, ':', 1) = 'TOTAL' AND r.OBS_VALUE IS NOT NULL
),
eupop AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS pop
    FROM {{source:eurostat-demo-gind}}
    WHERE split_part(indic_de, ':', 1) = 'AVG' AND OBS_VALUE IS NOT NULL
)
SELECT 'departement' AS maille, dep AS code, libelle, periode, round(1e6 * tues / pop, 1) AS valeur
FROM dep
UNION ALL
SELECT 'france', 'FR', 'France (départements, hors collectivités d''outre-mer)', periode, round(1e6 * sum(tues) / sum(pop), 1)
FROM dep
GROUP BY periode
UNION ALL
SELECT 'pays', eu.code, eu.libelle, eu.periode, round(1e6 * eu.tues / eupop.pop, 1)
FROM eu JOIN eupop USING (code, periode)
WHERE eupop.pop > 0
