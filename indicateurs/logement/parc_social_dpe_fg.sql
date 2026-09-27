-- Part des logements sociaux classés F ou G au DPE énergie, parmi ceux dont l'étiquette est renseignée (RPLS).
WITH r AS (
    SELECT DEP_CODE AS dep, left(millesime, 4) AS periode, DPEENERGIE AS dpe
    FROM {{source:sdes-rpls-logements}}
    WHERE DPEENERGIE IN ('A', 'B', 'C', 'D', 'E', 'F', 'G')
)
SELECT 'departement' AS maille, r.dep AS code, d.LIBELLE AS libelle, r.periode,
       round(100 * count(*) FILTER (WHERE r.dpe IN ('F', 'G')) / count(*), 1) AS valeur
FROM r JOIN {{source:insee-cog-departements}} AS d ON r.dep = d.DEP
GROUP BY r.dep, d.LIBELLE, r.periode
UNION ALL
SELECT 'france', 'FR', 'France métropolitaine', periode,
       round(100 * count(*) FILTER (WHERE dpe IN ('F', 'G')) / count(*), 1)
FROM r
GROUP BY periode
