-- Part des démarches essentielles en ligne dont la prise en compte du handicap est totale (Observatoire DINUM).
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, periode,
       round(100 * count(*) FILTER (WHERE handicap = 'Totale') / count(*), 1) AS valeur
FROM {{source:dinum-observatoire-demarches}}
WHERE en_ligne = 'Oui'
GROUP BY periode
