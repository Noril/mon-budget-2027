-- Solde des échanges de produits alimentaires, boissons et tabacs (CTCI 0 + 1), en milliards d'euros (Eurostat).
-- États membres : échanges avec le monde entier ; agrégat EU27_2020 : échanges hors UE.
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) / 1000 AS valeur
    FROM {{source:eurostat-ext-lt-intratrd}}
    WHERE split_part(indic_et, ':', 1) = 'MIO_BAL_VAL' AND split_part(sitc06, ':', 1) = 'SITC0_1' AND OBS_VALUE IS NOT NULL
      AND split_part(partner, ':', 1) = CASE WHEN split_part(geo, ':', 1) = 'EU27_2020' THEN 'EXT_EU27_2020' ELSE 'WORLD' END
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
