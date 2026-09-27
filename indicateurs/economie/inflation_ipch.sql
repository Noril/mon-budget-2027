-- Inflation annuelle moyenne mesurée par l'IPCH (Eurostat prc_hicp_aind). France = geo FR.
WITH v AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-prc-hicp-aind}}
    WHERE split_part(unit, ':', 1) = 'RCH_A_AVG'
      AND split_part(coicop, ':', 1) = 'CP00'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
