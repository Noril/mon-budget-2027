-- PIB nominal de la France (INSEE, comptes nationaux annuels), en milliards d'euros courants.
-- DISTINCT : la même série figure dans plusieurs tableaux du jeu ; une révision divergente créerait un doublon
-- (période en double), que pipelines.indicateurs refuse.
SELECT DISTINCT
    'france' AS maille,
    'FR' AS code,
    'France' AS libelle,
    TIME_PERIOD AS periode,
    CAST(OBS_VALUE AS DOUBLE) / 1000 AS valeur
FROM {{source:insee-pib}}
WHERE STO = 'B1GQ' AND PRICES = 'V' AND UNIT_MEASURE = 'XDC' AND TRANSFORMATION = 'N'
  AND COUNTERPART_AREA = 'W0' AND OBS_VALUE IS NOT NULL
