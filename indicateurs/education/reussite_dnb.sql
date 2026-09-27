-- Taux de réussite au brevet : admis / présents, toutes séries et deux sexes confondus.
WITH d AS (
    SELECT CAST(year(session) AS VARCHAR) AS periode, dep_sco, presents, admis
    FROM {{source:depp-dnb-departements}}
)
SELECT 'departement' AS maille, d.dep_sco AS code, c.LIBELLE AS libelle, d.periode,
       round(100 * sum(d.admis) / sum(d.presents), 1) AS valeur
FROM d JOIN {{source:insee-cog-departements}} AS c ON d.dep_sco = c.DEP
GROUP BY d.dep_sco, c.LIBELLE, d.periode
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(100 * sum(admis) / sum(presents), 1)
FROM d
GROUP BY periode
