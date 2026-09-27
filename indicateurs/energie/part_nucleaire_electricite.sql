-- Part du nucléaire dans la production brute d'électricité, en % (Eurostat, bilans énergétiques).
WITH e AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           max(CASE WHEN split_part(siec, ':', 1) = 'N900H' THEN CAST(OBS_VALUE AS DOUBLE) END) AS nucleaire,
           max(CASE WHEN split_part(siec, ':', 1) = 'TOTAL' THEN CAST(OBS_VALUE AS DOUBLE) END) AS total
    FROM {{source:eurostat-nrg-bal-peh}}
    WHERE split_part(nrg_bal, ':', 1) = 'GEP' AND split_part(unit, ':', 1) = 'GWH'
    GROUP BY ALL
),
v AS (SELECT code, libelle, periode, 100 * nucleaire / total AS valeur FROM e WHERE nucleaire IS NOT NULL AND total > 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
