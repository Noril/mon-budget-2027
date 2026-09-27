-- Dette publique au sens de Maastricht en % du PIB (Eurostat, notification PDE). France = geo FR.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        CAST(TIME_PERIOD AS INTEGER) AS annee,
        max(CASE WHEN split_part(na_item, ':', 1) = 'GD' THEN CAST(OBS_VALUE AS DOUBLE) END) AS dette,
        max(CASE WHEN split_part(na_item, ':', 1) = 'D41PAY' THEN CAST(OBS_VALUE AS DOUBLE) END) AS interets,
        max(CASE WHEN split_part(na_item, ':', 1) = 'B1GQ' THEN CAST(OBS_VALUE AS DOUBLE) END) AS pib
    FROM {{source:eurostat-gov-10dd-edpt1}}
    WHERE split_part(unit, ':', 1) = 'MIO_NAC'
      AND concat_ws('/', split_part(sector, ':', 1), split_part(na_item, ':', 1)) IN ('S13/B9', 'S13/GD', 'S13/D41PAY', 'S1/B1GQ')
    GROUP BY ALL
),
v AS (SELECT code, libelle, CAST(annee AS VARCHAR) AS periode, 100 * dette / pib AS valeur FROM e
      WHERE dette IS NOT NULL AND pib IS NOT NULL AND pib <> 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
