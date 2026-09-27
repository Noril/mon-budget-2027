-- Premiers titres de séjour délivrés pour 1 000 habitants : Eurostat migr_resfirst / population au 1er janvier (demo_gind).
WITH n AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS nombre
    FROM {{source:eurostat-migr-resfirst}}
    WHERE split_part(reason, ':', 1) = 'TOTAL' AND split_part(citizen, ':', 1) = 'TOTAL' AND split_part(duration, ':', 1) = 'TOTAL' AND split_part(unit, ':', 1) = 'PER' AND OBS_VALUE IS NOT NULL
),
p AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS population
    FROM {{source:eurostat-population-1er-janvier}}
    WHERE split_part(indic_de, ':', 1) = 'JAN' AND OBS_VALUE IS NOT NULL
),
v AS (SELECT n.*, round(1e3 * n.nombre / p.population, 1) AS valeur FROM n JOIN p USING (code, periode) WHERE p.population > 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
