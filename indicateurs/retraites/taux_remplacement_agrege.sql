-- Taux de remplacement agrégé (Eurostat EU-SILC), exprimé en %. France = geo FR.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code,
           substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode,
           round(100 * CAST(OBS_VALUE AS DOUBLE), 1) AS valeur
    FROM {{source:eurostat-ilc-pnp3}}
    WHERE split_part(sex, ':', 1) = 'T'
      AND split_part(unit, ':', 1) = 'PC'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
