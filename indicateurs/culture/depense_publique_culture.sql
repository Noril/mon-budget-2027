-- Dépenses des administrations publiques en services culturels (COFOG GF0802), en % du PIB.
-- Numérateur : gov_10a_exp, millions d'euros ; dénominateur : PIB nama_10_gdp, millions d'euros courants.
WITH dep AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS depense
    FROM {{source:eurostat-gov-10a-exp-culture}}
    WHERE split_part(unit, ':', 1) = 'MIO_EUR' AND split_part(cofog99, ':', 1) = 'GF0802'
      AND split_part(na_item, ':', 1) = 'TE' AND split_part(sector, ':', 1) = 'S13' AND OBS_VALUE IS NOT NULL
),
pib AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS pib
    FROM {{source:eurostat-nama-10-gdp-echanges}}
    WHERE split_part(unit, ':', 1) = 'CP_MEUR' AND split_part(na_item, ':', 1) = 'B1GQ' AND OBS_VALUE IS NOT NULL
),
v AS (
    SELECT d.code, d.libelle, d.periode, round(100 * d.depense / p.pib, 3) AS valeur
    FROM dep AS d JOIN pib AS p ON d.code = p.code AND d.periode = p.periode
    WHERE p.pib > 0
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
