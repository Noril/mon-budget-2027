-- Taux de chômage au sens du BIT, moyenne annuelle.
-- France : enquête Emploi de l'INSEE (15 ans ou plus, hors Mayotte). Pays : Eurostat une_rt_a (15-74 ans).
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, TIME_PERIOD AS periode,
       CAST(OBS_VALUE AS DOUBLE) AS valeur
FROM {{source:insee-eec-series}}
WHERE EEC_MEASURE = 'UNEMPRATE' AND SEX = '_T' AND AGE = '_T' AND EMPSTA = '2'
  AND EMPFORM = '_T' AND PCS = '_T' AND EDUC = '_T' AND WKTIME = '_T'
  AND UNDEREMP = '_T' AND UNEMPDUR = '_T' AND COMPOHALO = '_T'
  AND OBS_VALUE IS NOT NULL
UNION ALL
SELECT 'pays', split_part(geo, ':', 1), substr(geo, strpos(geo, ':') + 1), TIME_PERIOD, CAST(OBS_VALUE AS DOUBLE)
FROM {{source:eurostat-une-rt-a}}
WHERE split_part(age, ':', 1) = 'Y15-74' AND split_part(unit, ':', 1) = 'PC_ACT' AND split_part(sex, ':', 1) = 'T'
  AND OBS_VALUE IS NOT NULL
