-- Taux d'emploi des 20-64 ans (Eurostat lfsi_emp_a). France = geo FR.
WITH v AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-lfsi-emp-a}}
    WHERE split_part(indic_em, ':', 1) = 'EMP_LFS' AND split_part(sex, ':', 1) = 'T'
      AND split_part(age, ':', 1) = 'Y20-64' AND split_part(unit, ':', 1) = 'PC_POP'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
