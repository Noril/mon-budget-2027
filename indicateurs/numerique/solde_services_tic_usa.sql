-- Solde des échanges de services TIC (poste SI) avec les États-Unis, en milliards d'euros.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) / 1000 AS valeur
    FROM {{source:eurostat-bop-its6-det}}
    WHERE split_part(currency, ':', 1) = 'MIO_EUR'
      AND split_part(bop_item, ':', 1) = 'SI'
      AND split_part(stk_flow, ':', 1) = 'BAL'
      AND split_part(partner, ':', 1) = 'US'
      AND nullif(OBS_VALUE, '') IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM e WHERE code = 'FR'
