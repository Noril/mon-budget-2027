-- Capacité opérationnelle des établissements pénitentiaires au 1er du mois, France entière (Tab6).
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, substr(date, 1, 7) AS periode, valeur
FROM {{source:justice-ecroues-mensuel}}
WHERE tableau = 'Tab6' AND mesure = 'capacite_operationnelle' AND niveau = 'Total France entière'
