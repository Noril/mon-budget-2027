-- Évolution sur un an de l'emploi salarié privé au 31 décembre (URSSAF), en %.
WITH long AS (
    SELECT code_departement, CAST(right(colonne, 4) AS INTEGER) AS annee, CAST(effectif AS DOUBLE) AS effectif
    FROM (
        UNPIVOT (SELECT code_departement, COLUMNS('^effectifs_salaries_\d{4}$') FROM {{source:urssaf-effectifs-departements}})
        ON COLUMNS('^effectifs_salaries_\d{4}$') INTO NAME colonne VALUE effectif
    )
),
dep AS (
    SELECT l.code_departement AS DEP, d.LIBELLE, d.REG, l.annee, sum(l.effectif) AS effectif
    FROM long AS l LEFT JOIN {{source:insee-cog-departements}} AS d ON l.code_departement = d.DEP
    GROUP BY ALL
),
niveaux AS (
    SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, annee, sum(effectif) AS effectif
    FROM dep GROUP BY annee
    UNION ALL
    SELECT 'region', dep.REG, r.LIBELLE, dep.annee, sum(dep.effectif)
    FROM dep JOIN {{source:insee-cog-regions}} AS r ON dep.REG = r.REG
    GROUP BY ALL
    UNION ALL
    SELECT 'departement', DEP, LIBELLE, annee, effectif FROM dep WHERE LIBELLE IS NOT NULL
)
SELECT n.maille, n.code, n.libelle, CAST(n.annee AS VARCHAR) AS periode,
       round(100 * (n.effectif / p.effectif - 1), 2) AS valeur
FROM niveaux AS n
JOIN niveaux AS p ON p.maille = n.maille AND p.code = n.code AND p.annee = n.annee - 1
WHERE p.effectif > 0
