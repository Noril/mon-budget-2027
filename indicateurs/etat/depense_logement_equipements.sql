-- Dépenses des APU pour la fonction COFOG GF06 (Logements et équipements collectifs), en % du PIB, telles que publiées par Eurostat (gov_10a_exp).
WITH v AS (
    SELECT DISTINCT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-gov-10a-exp}}
    WHERE split_part(unit, ':', 1) = 'PC_GDP' AND split_part(sector, ':', 1) = 'S13'
      AND split_part(cofog99, ':', 1) = 'GF06' AND split_part(na_item, ':', 1) = 'TE'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
