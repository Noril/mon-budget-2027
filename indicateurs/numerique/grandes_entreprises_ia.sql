-- Entreprises de 250 salariés ou plus utilisant au moins une technologie d'IA (Eurostat isoc_eb_ai). France = geo FR.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-isoc-eb-ai}}
    WHERE split_part(size_emp, ':', 1) = 'GE250'
      AND split_part(nace_r2, ':', 1) = 'C10-S951_X_K'
      AND split_part(indic_is, ':', 1) = 'E_AI_TANY'
      AND split_part(unit, ':', 1) = 'PC_ENT'
      AND nullif(OBS_VALUE, '') IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM e WHERE code = 'FR'
