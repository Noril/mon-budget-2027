-- Part du rail dans le transport terrestre intérieur de marchandises (tonnes-km), en % (Eurostat).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-tran-hv-frmod}}
    WHERE split_part(tra_mode, ':', 1) = 'RAIL'
      AND split_part(unit, ':', 1) = 'PC' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
