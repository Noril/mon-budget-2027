-- Part des 25-34 ans diplômés du supérieur (CITE 5-8), Eurostat edat_lfse_03. France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           CAST(TIME_PERIOD AS VARCHAR) AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-edat-lfse-03}}
    WHERE split_part(sex, ':', 1) = 'T' AND split_part(age, ':', 1) = 'Y25-34'
      AND split_part(unit, ':', 1) = 'PC' AND split_part(isced11, ':', 1) = 'ED5-8'
      AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> ''
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
