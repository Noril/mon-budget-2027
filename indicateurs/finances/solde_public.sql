-- Solde public (capacité ou besoin de financement des APU) en % du PIB.
-- France : INSEE (millésime le plus récent). Pays : Eurostat, notification PDE.
-- DD_CNA_APU : depuis 2023, les séries « consolidées » de dépenses, recettes et intérêts reprennent les montants non
-- consolidés (voir le catalogue) ; seul le solde B9, invariant par consolidation, est lu ici. Garde-fou : B9 consolidé
-- et non consolidé doivent coïncider chaque année où les deux sont publiés, sinon le calcul échoue.
WITH b9_brut AS (
    SELECT DISTINCT CONSOLIDATION AS conso, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS montant
    FROM {{source:insee-comptes-apu}}
    WHERE REF_SECTOR = 'S13' AND STO = 'B9' AND CONSOLIDATION IN ('C', 'N') AND ACCOUNTING_ENTRY = 'B'
      AND EXPENDITURE = '_Z' AND UNIT_MEASURE = 'XDC' AND OBS_VALUE IS NOT NULL
),
garde AS (
    SELECT count(*) AS ecarts
    FROM b9_brut c JOIN b9_brut n ON c.periode = n.periode AND c.conso = 'C' AND n.conso = 'N'
    WHERE abs(c.montant - n.montant) > 0.5
),
b9 AS (
    SELECT periode, montant FROM b9_brut, garde
    WHERE conso = 'C'
      AND (ecarts = 0 OR error('insee-comptes-apu : B9 consolidé différent du non consolidé, série à revoir'))
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
