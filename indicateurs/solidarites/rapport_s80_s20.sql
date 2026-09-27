-- Rapport interquintile S80/S20 du revenu disponible équivalent (Eurostat EU-SILC). France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code,
           substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-ilc-di11}}
    WHERE split_part(age, ':', 1) = 'TOTAL'
      AND split_part(sex, ':', 1) = 'T'
      AND split_part(unit, ':', 1) = 'RAT'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
