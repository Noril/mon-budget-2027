-- Part de la FBCF (P51G) dans les dépenses totales (TE) de la fonction Défense (COFOG GF02), en millions d'euros.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        max(CASE WHEN split_part(na_item, ':', 1) = 'P51G' THEN CAST(OBS_VALUE AS DOUBLE) END) AS fbcf,
        max(CASE WHEN split_part(na_item, ':', 1) = 'TE' THEN CAST(OBS_VALUE AS DOUBLE) END) AS total
    FROM {{source:eurostat-gov-10a-exp-defense}}
    WHERE split_part(unit, ':', 1) = 'MIO_EUR' AND split_part(sector, ':', 1) = 'S13'
      AND split_part(cofog99, ':', 1) = 'GF02'
    GROUP BY ALL
),
v AS (SELECT code, libelle, periode, 100 * fbcf / total AS valeur FROM e
      WHERE fbcf IS NOT NULL AND total IS NOT NULL AND total <> 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
