-- Solde public (capacité ou besoin de financement des APU) en % du PIB.
-- France : INSEE (millésime le plus récent). Pays : Eurostat, notification PDE.
WITH b9 AS (
    SELECT DISTINCT TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS montant
    FROM {{source:insee-comptes-apu}}
    WHERE REF_SECTOR = 'S13' AND STO = 'B9' AND CONSOLIDATION = 'C' AND ACCOUNTING_ENTRY = 'B'
      AND EXPENDITURE = '_Z' AND UNIT_MEASURE = 'XDC' AND OBS_VALUE IS NOT NULL
),
pib AS (
    SELECT DISTINCT TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS montant
    FROM {{source:insee-pib}}
    WHERE STO = 'B1GQ' AND PRICES = 'V' AND UNIT_MEASURE = 'XDC' AND TRANSFORMATION = 'N'
      AND COUNTERPART_AREA = 'W0' AND OBS_VALUE IS NOT NULL
),
eurostat AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        max(CASE WHEN split_part(na_item, ':', 1) = 'B9' THEN CAST(OBS_VALUE AS DOUBLE) END) AS b9,
        max(CASE WHEN split_part(na_item, ':', 1) = 'B1GQ' THEN CAST(OBS_VALUE AS DOUBLE) END) AS pib
    FROM {{source:eurostat-gov-10dd-edpt1}}
    WHERE split_part(unit, ':', 1) = 'MIO_NAC'
      AND concat_ws('/', split_part(sector, ':', 1), split_part(na_item, ':', 1)) IN ('S13/B9', 'S13/GD', 'S13/D41PAY', 'S1/B1GQ')
    GROUP BY ALL
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, b9.periode, 100 * b9.montant / pib.montant AS valeur
FROM b9 JOIN pib USING (periode)
UNION ALL
SELECT 'pays', code, libelle, periode, 100 * b9 / pib
FROM eurostat
WHERE b9 IS NOT NULL AND pib IS NOT NULL AND pib <> 0
