-- Dépenses de fonctionnement des départements (budgets principal et annexes consolidés, OFGL), en euros par habitant.
-- Champ : conseils départementaux et Collectivité européenne d'Alsace (categ = DEPT) ; Métropole de Lyon et Ville de
-- Paris depuis 2019 (compétences communales ou intercommunales mêlées) écartées.
WITH d AS (
    SELECT year(exer) AS annee, dep_code, siren, montant, ptot
    FROM {{source:ofgl-departements-consolides}}
    WHERE agregat = 'Dépenses de fonctionnement' AND categ = 'DEPT' AND montant IS NOT NULL AND ptot > 0
),
-- Alsace : Bas-Rhin et Haut-Rhin jusqu'en 2020, puis une collectivité unique rattachée aux deux départements
geo AS (
    SELECT annee, montant, ptot,
        unnest(CASE WHEN siren = '226700011' THEN ['67'] WHEN siren = '226800019' THEN ['68']
                    WHEN dep_code = '67A' THEN ['67', '68'] ELSE [dep_code] END) AS DEP
    FROM d
)
SELECT 'france' AS maille, 'FR' AS code, 'Départements (hors Paris et Métropole de Lyon)' AS libelle,
       CAST(annee AS VARCHAR) AS periode, round(sum(montant) / sum(ptot), 2) AS valeur
FROM d WHERE dep_code <> '75'
GROUP BY annee
UNION ALL
SELECT 'departement', c.DEP, c.LIBELLE, CAST(g.annee AS VARCHAR), round(sum(g.montant) / sum(g.ptot), 2)
FROM geo AS g JOIN {{source:insee-cog-departements}} AS c ON g.DEP = c.DEP
GROUP BY c.DEP, c.LIBELLE, g.annee
