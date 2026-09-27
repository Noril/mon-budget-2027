-- Part des boursiers parmi les néo-bacheliers admis en classe préparatoire aux grandes écoles via Parcoursup.
-- Département = département de la CPGE.
WITH p AS (SELECT session AS periode, dep, acc_neobac, acc_brs FROM {{source:sies-parcoursup}} WHERE fili = 'CPGE')
SELECT 'departement' AS maille, p.dep AS code, c.LIBELLE AS libelle, p.periode,
       round(100 * sum(p.acc_brs) / sum(p.acc_neobac), 1) AS valeur
FROM p JOIN {{source:insee-cog-departements}} AS c ON p.dep = c.DEP
GROUP BY p.dep, c.LIBELLE, p.periode
HAVING sum(p.acc_neobac) > 0
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(100 * sum(acc_brs) / sum(acc_neobac), 1)
FROM p
GROUP BY periode
