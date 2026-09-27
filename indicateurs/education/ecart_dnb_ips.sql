-- Écart de réussite au brevet (série générale) entre le quart des collèges les plus favorisés et le quart
-- des plus défavorisés selon l'IPS de l'année scolaire de la session (session 2025 -> rentrée 2024-2025).
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
colleges AS (
    SELECT CAST(CAST(left(i.rentree_scolaire, 4) AS INTEGER) + 1 AS VARCHAR) AS periode, i.uai, i.ips
    FROM {{source:depp-ips-colleges}} AS i
    JOIN geo AS g ON i.code_insee_de_la_commune = g.COM
    WHERE i.ips IS NOT NULL
),
seuils AS (
    SELECT periode, quantile_cont(ips, 0.25) AS q1, quantile_cont(ips, 0.75) AS q3 FROM colleges GROUP BY periode
),
dnb AS (
    SELECT c.periode, v.nb_candidats_g AS n, v.taux_de_reussite_g AS taux,
           CASE WHEN c.ips < s.q1 THEN 'defavorise' WHEN c.ips > s.q3 THEN 'favorise' END AS quart
    FROM {{source:depp-va-colleges}} AS v
    JOIN colleges AS c ON c.uai = v.uai AND c.periode = CAST(year(v.session) AS VARCHAR)
    JOIN seuils AS s ON s.periode = c.periode
    WHERE v.nb_candidats_g > 0 AND v.taux_de_reussite_g IS NOT NULL
)
SELECT 'france' AS maille, 'FR' AS code, 'France (hors COM)' AS libelle, periode,
       round(sum(n * taux) FILTER (WHERE quart = 'favorise') / sum(n) FILTER (WHERE quart = 'favorise')
           - sum(n * taux) FILTER (WHERE quart = 'defavorise') / sum(n) FILTER (WHERE quart = 'defavorise'), 1) AS valeur
FROM dnb
GROUP BY periode
