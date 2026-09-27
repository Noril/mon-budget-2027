-- Personnes écrouées détenues au 1er du mois, France entière (métropole et outre-mer).
-- Tab2 de chaque classeur mensuel couvre 25 mois : pour un mois donné, on garde la valeur du classeur le plus récent.
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, substr(date, 1, 7) AS periode, valeur
FROM {{source:justice-ecroues-mensuel}}
WHERE tableau = 'Tab2' AND mesure = 'detenus' AND niveau = 'Total France entière'
QUALIFY row_number() OVER (PARTITION BY date ORDER BY date_fichier DESC) = 1
