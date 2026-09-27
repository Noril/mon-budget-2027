-- Taux d'intérêt apparent de la dette : intérêts versés de l'année / dette de fin d'année précédente (Eurostat).
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
v AS (
    SELECT c.code, c.libelle, CAST(c.annee AS VARCHAR) AS periode, 100 * c.interets / p.dette AS valeur
    FROM e AS c JOIN e AS p ON p.code = c.code AND p.annee = c.annee - 1
    WHERE c.interets IS NOT NULL AND p.dette IS NOT NULL AND p.dette <> 0
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
