-- Effectifs salariés du secteur privé au 31 décembre (URSSAF), par département, région (COG 2026) et France.
-- Format large (une colonne effectifs_salaries_AAAA par année) remis en long.
WITH long AS (
    SELECT code_departement, CAST(right(colonne, 4) AS VARCHAR) AS periode, CAST(effectif AS DOUBLE) AS effectif
    FROM (
        UNPIVOT (SELECT code_departement, COLUMNS('^effectifs_salaries_\d{4}$') FROM {{source:urssaf-effectifs-departements}})
        ON COLUMNS('^effectifs_salaries_\d{4}$') INTO NAME colonne VALUE effectif
    )
),
dep AS (
    SELECT l.code_departement AS DEP, d.LIBELLE, d.REG, l.periode, sum(l.effectif) AS effectif
    FROM long AS l LEFT JOIN {{source:insee-cog-departements}} AS d ON l.code_departement = d.DEP
    GROUP BY ALL
)
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, periode, round(sum(effectif), 0) AS valeur
FROM dep GROUP BY periode
UNION ALL
SELECT 'region', dep.REG, r.LIBELLE, dep.periode, round(sum(dep.effectif), 0)
FROM dep JOIN {{source:insee-cog-regions}} AS r ON dep.REG = r.REG
GROUP BY ALL
UNION ALL
SELECT 'departement', DEP, LIBELLE, periode, round(effectif, 0)
FROM dep WHERE LIBELLE IS NOT NULL
