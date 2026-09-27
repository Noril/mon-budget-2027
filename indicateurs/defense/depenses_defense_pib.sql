-- Dépenses des APU de la fonction Défense (COFOG GF02, total TE) en % du PIB, telles que publiées par Eurostat.
WITH v AS (
    SELECT DISTINCT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-gov-10a-exp-defense}}
    WHERE split_part(unit, ':', 1) = 'PC_GDP' AND split_part(sector, ':', 1) = 'S13'
      AND split_part(cofog99, ':', 1) = 'GF02' AND split_part(na_item, ':', 1) = 'TE' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
