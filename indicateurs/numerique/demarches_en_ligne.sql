-- Part des démarches essentielles suivies par l'Observatoire DINUM entièrement réalisables en ligne, par édition.
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, periode,
       round(100 * count(*) FILTER (WHERE en_ligne = 'Oui') / count(*), 1) AS valeur
FROM {{source:dinum-observatoire-demarches}}
GROUP BY periode
