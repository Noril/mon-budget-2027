-- Taux de risque de pauvreté au seuil de 60 % du revenu équivalent médian (Eurostat EU-SILC). France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code,
           substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-ilc-li02}}
    WHERE split_part(statinfo, ':', 1) = 'MED_EI'
      AND split_part(unit, ':', 1) = 'PC'
      AND split_part(rskpovth, ':', 1) = 'B_60'
      AND split_part(sex, ':', 1) = 'T'
      AND split_part(age, ':', 1) = 'TOTAL'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
