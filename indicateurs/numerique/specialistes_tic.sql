-- Spécialistes TIC en % de l'emploi total (Eurostat isoc_sks_itspt). France = geo FR.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-isoc-sks-itspt}}
    WHERE split_part(unit, ':', 1) = 'PC_EMP'
      AND nullif(OBS_VALUE, '') IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM e WHERE code = 'FR'
