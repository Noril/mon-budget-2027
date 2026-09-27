-- Dépense intérieure de R&D, tous secteurs d'exécution, en % du PIB (Eurostat rd_e_gerdtot). France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           CAST(TIME_PERIOD AS VARCHAR) AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-rd-e-gerdtot}}
    WHERE split_part(sectperf, ':', 1) = 'TOTAL' AND split_part(unit, ':', 1) = 'PC_GDP'
      AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> ''
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
