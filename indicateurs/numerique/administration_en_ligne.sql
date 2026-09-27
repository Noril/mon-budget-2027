-- Particuliers de 16 à 74 ans ayant interagi en ligne avec une administration dans les douze derniers mois (Eurostat isoc_ciegi_ac).
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-isoc-ciegi-ac}}
    WHERE split_part(indic_is, ':', 1) = 'I_IUGOV1'
      AND split_part(unit, ':', 1) = 'PC_IND'
      AND split_part(ind_type, ':', 1) = 'IND_TOTAL'
      AND nullif(OBS_VALUE, '') IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM e WHERE code = 'FR'
