-- Inflation annuelle moyenne mesurée par l'IPC de l'INSEE : France entière et départements d'outre-mer.
WITH v AS (
    SELECT GEO, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:insee-ipc}}
    WHERE IDX_TYPE = 'CPI' AND IND_TYPE = 'Y_VAR' AND FREQ = 'A'
      AND COICOP_2018 = '00' AND TPH_CPI = '_T' AND SEASONAL_ADJUST = 'N' AND PRODUCT_GROUP = '_Z'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, periode, valeur FROM v WHERE GEO = 'F'
UNION ALL
SELECT 'departement', v.GEO, d.LIBELLE, v.periode, v.valeur
FROM v JOIN {{source:insee-cog-departements}} AS d ON v.GEO = d.DEP
