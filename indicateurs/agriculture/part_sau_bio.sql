-- Part de la surface agricole utilisée en agriculture biologique (certifiée et en conversion), en % (Eurostat).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-org-cropar}}
    WHERE split_part(unit, ':', 1) = 'PC_UAA'
      AND split_part(crops, ':', 1) = 'UAAXK0000'
      AND split_part(agprdmet, ':', 1) = 'TOTAL' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
