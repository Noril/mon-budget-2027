-- Indice du revenu réel des facteurs de l'agriculture par UTA, base 2010 = 100 (Eurostat, indicateur A).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-aact-eaa06}}
    WHERE split_part(indic_agr, ':', 1) = 'IND_A'
      AND split_part(unit, ':', 1) = 'I10' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
