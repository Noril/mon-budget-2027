-- Taux de pauvreté officiel (ERFS, séries rétropolées), France métropolitaine, ensemble de la population.
SELECT 'france' AS maille, 'FR' AS code, 'France métropolitaine' AS libelle,
       TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
FROM {{source:insee-erfs-retropole}}
WHERE ERFS_MEASURE = 'PR_MD60'
  AND GEO = 'FM'
  AND EMPSTA_ENQ = '_T' AND AGE = '_T' AND TPH = '_T' AND MUN_DENSITY_LEVEL = '_T'
  AND OBS_VALUE IS NOT NULL
