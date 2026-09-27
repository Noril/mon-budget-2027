-- Part du train dans le transport terrestre intérieur de voyageurs (voyageurs-km), en % (Eurostat).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-tran-hv-psmod}}
    WHERE split_part(vehicle, ':', 1) = 'TRN'
      AND split_part(unit, ':', 1) = 'PC' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
