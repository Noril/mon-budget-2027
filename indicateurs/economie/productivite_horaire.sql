-- Productivité nominale du travail par heure travaillée, en SPA (Eurostat nama_10_lp_ulc). France = geo FR.
WITH v AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-nama-10-lp-ulc}}
    WHERE split_part(unit, ':', 1) = 'CP_MPPS_EU27_2020'
      AND split_part(na_item, ':', 1) = 'NLPR_HW'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
