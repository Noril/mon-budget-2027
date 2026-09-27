-- Solde des échanges extérieurs de biens en % du PIB (comptes nationaux, Eurostat nama_10_gdp). France = geo FR.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        max(CASE WHEN split_part(na_item, ':', 1) = 'P61' THEN CAST(OBS_VALUE AS DOUBLE) END) AS exportations,
        max(CASE WHEN split_part(na_item, ':', 1) = 'P71' THEN CAST(OBS_VALUE AS DOUBLE) END) AS importations,
        max(CASE WHEN split_part(na_item, ':', 1) = 'B1GQ' THEN CAST(OBS_VALUE AS DOUBLE) END) AS pib
    FROM {{source:eurostat-nama-10-gdp-echanges}}
    WHERE split_part(unit, ':', 1) = 'CP_MEUR'
    GROUP BY ALL
),
v AS (
    SELECT code, libelle, periode, round(100 * (exportations - importations) / pib, 2) AS valeur
    FROM e
    WHERE exportations IS NOT NULL AND importations IS NOT NULL AND pib IS NOT NULL AND pib <> 0
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
