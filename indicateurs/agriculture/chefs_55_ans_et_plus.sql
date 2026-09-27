-- Part des exploitations dont le chef a 55 ans ou plus, en % (Eurostat, enquêtes sur la structure des exploitations).
WITH e AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           max(CASE WHEN split_part(age, ':', 1) = 'TOTAL' THEN CAST(OBS_VALUE AS DOUBLE) END) AS total,
           max(CASE WHEN split_part(age, ':', 1) = 'Y55-64' THEN CAST(OBS_VALUE AS DOUBLE) END) AS a55_64,
           max(CASE WHEN split_part(age, ':', 1) = 'Y_GE65' THEN CAST(OBS_VALUE AS DOUBLE) END) AS a65
    FROM {{source:eurostat-ef-m-farmang}}
    WHERE split_part(statinfo, ':', 1) = 'TOTAL' AND split_part(sex, ':', 1) = 'T'
      AND split_part(so_eur, ':', 1) = 'TOTAL' AND split_part(uaarea, ':', 1) = 'TOTAL' AND split_part(unit, ':', 1) = 'HLD'
      AND (length(split_part(geo, ':', 1)) = 2 OR split_part(geo, ':', 1) LIKE 'EU%')
    GROUP BY ALL
),
v AS (SELECT code, libelle, periode, 100 * (a55_64 + a65) / total AS valeur FROM e
      WHERE total > 0 AND a55_64 IS NOT NULL AND a65 IS NOT NULL)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
