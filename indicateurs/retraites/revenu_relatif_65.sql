-- Revenu médian relatif des 65 ans ou plus (Eurostat EU-SILC), exprimé en % du revenu médian des moins de 65 ans. France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code,
           substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode,
           round(100 * CAST(OBS_VALUE AS DOUBLE), 1) AS valeur
    FROM {{source:eurostat-ilc-pnp2}}
    WHERE split_part(statinfo, ':', 1) = 'R_MED_I'
      AND split_part(age, ':', 1) = 'Y_GE65'
      AND split_part(sex, ':', 1) = 'T'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
