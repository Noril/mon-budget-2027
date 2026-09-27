-- Militaires de carrière et sous contrat du ministère des Armées, hors gendarmerie, en ETPT (toutes catégories).
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, CAST(annee AS VARCHAR) AS periode, sum(etpt) AS valeur
FROM {{source:armees-militaires-carriere-contrat}}
WHERE categorie = 'ensemble' AND armee = 'Total (hors gendarmerie)' AND statut IN ('carrière', 'contrat')
GROUP BY annee
HAVING count(*) = 2
