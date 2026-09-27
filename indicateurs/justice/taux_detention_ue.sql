-- Personnes détenues pour 100 000 habitants (Eurostat crim_pris_cap / population au 1er janvier, demo_gind).
WITH d AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS detenus
    FROM {{source:eurostat-crim-pris-cap}}
    WHERE split_part(indic_cr, ':', 1) = 'PRIS_ACT_CAP' AND split_part(unit, ':', 1) = 'NR' AND OBS_VALUE IS NOT NULL
),
p AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS population
    FROM {{source:eurostat-demo-gind}}
    WHERE split_part(indic_de, ':', 1) = 'JAN' AND OBS_VALUE IS NOT NULL
),
v AS (SELECT d.*, p.population FROM d JOIN p USING (code, periode) WHERE p.population > 0),
ue AS (
    SELECT 'EU27_2020' AS code, 'Union européenne - 27 pays (à partir de 2020)' AS libelle, periode,
           sum(detenus) AS detenus, sum(population) AS population
    FROM v
    WHERE code IN ('AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU', 'IE', 'IT',
                   'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK')
    GROUP BY periode
    HAVING count(*) = 27
)
SELECT 'pays' AS maille, code, libelle, periode, round(1e5 * detenus / population, 1) AS valeur FROM v
UNION ALL
SELECT 'pays', code, libelle, periode, round(1e5 * detenus / population, 1) FROM ue
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(1e5 * detenus / population, 1) FROM v WHERE code = 'FR'
