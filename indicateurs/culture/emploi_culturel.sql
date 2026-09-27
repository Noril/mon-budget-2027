-- Emploi culturel en % de l'emploi total (Eurostat cult_emp_sex, deux sexes).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-cult-emp-sex}}
    WHERE split_part(unit, ':', 1) = 'PC_EMP' AND split_part(sex, ':', 1) = 'T' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
