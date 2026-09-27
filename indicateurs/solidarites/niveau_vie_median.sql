-- Niveau de vie médian annuel (Filosofi), France métropolitaine, région, département.
-- Cellules soumises au secret statistique (CONF_STATUS = C) ou manquantes (OBS_VALUE vide) exclues.
WITH f AS (
    SELECT GEO_OBJECT, GEO, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:insee-filosofi}}
    WHERE FILOSOFI_MEASURE = 'MED_SL'
      AND GEO_OBJECT IN ('FRANCE', 'REG', 'DEP')
      AND CONF_STATUS = 'F'
      AND OBS_VALUE IS NOT NULL
)
SELECT 'france' AS maille, 'FR' AS code, 'France métropolitaine' AS libelle, periode, valeur
FROM f WHERE GEO_OBJECT = 'FRANCE' AND GEO = 'FM'
UNION ALL
SELECT 'region', f.GEO, r.LIBELLE, f.periode, f.valeur
FROM f JOIN {{source:insee-cog-regions}} AS r ON f.GEO = r.REG
WHERE f.GEO_OBJECT = 'REG'
UNION ALL
SELECT 'departement', f.GEO, d.LIBELLE, f.periode, f.valeur
FROM f JOIN {{source:insee-cog-departements}} AS d ON f.GEO = d.DEP
WHERE f.GEO_OBJECT = 'DEP'
