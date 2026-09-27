-- Taux d'épargne brute des départements (épargne brute / recettes de fonctionnement, OFGL, comptes consolidés).
-- Même champ que etat.depenses_fonct_departements.
WITH d AS (
    SELECT year(exer) AS annee, dep_code, siren,
        sum(CASE WHEN agregat = 'Epargne brute' THEN montant END) AS epargne,
        sum(CASE WHEN agregat = 'Recettes de fonctionnement' THEN montant END) AS recettes
    FROM {{source:ofgl-departements-consolides}}
    WHERE agregat IN ('Epargne brute', 'Recettes de fonctionnement') AND categ = 'DEPT'
    GROUP BY ALL
    HAVING epargne IS NOT NULL AND recettes > 0
),
geo AS (
    SELECT annee, epargne, recettes,
        unnest(CASE WHEN siren = '226700011' THEN ['67'] WHEN siren = '226800019' THEN ['68']
                    WHEN dep_code = '67A' THEN ['67', '68'] ELSE [dep_code] END) AS DEP
    FROM d
)
SELECT 'france' AS maille, 'FR' AS code, 'Départements (hors Paris et Métropole de Lyon)' AS libelle,
       CAST(annee AS VARCHAR) AS periode, round(100 * sum(epargne) / sum(recettes), 2) AS valeur
FROM d WHERE dep_code <> '75'
GROUP BY annee
UNION ALL
SELECT 'departement', c.DEP, c.LIBELLE, CAST(g.annee AS VARCHAR), round(100 * sum(g.epargne) / sum(g.recettes), 2)
FROM geo AS g JOIN {{source:insee-cog-departements}} AS c ON g.DEP = c.DEP
GROUP BY c.DEP, c.LIBELLE, g.annee
