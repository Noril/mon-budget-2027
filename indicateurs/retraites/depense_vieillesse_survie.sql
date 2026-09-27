-- Prestations de protection sociale des fonctions vieillesse et survie en % du PIB (Eurostat SESPROS). France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code,
           substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-spr-exp-func}}
    WHERE split_part(spdeps, ':', 1) = 'SPR'
      AND split_part(spfunc, ':', 1) = 'OLD_SRV'
      AND split_part(unit, ':', 1) = 'PC_GDP'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
