-- Cambriolages de logement enregistrés, pour 1 000 logements. Base départementale SSMSI (faits constatés), format long.
-- Département : somme des indicateurs retenus / insee_log du département ; France : somme des départements.
WITH d AS (
    SELECT Code_departement AS dep, annee,
           sum(CAST(nombre AS DOUBLE)) AS nombre,
           -- insee_log est répété à l'identique sur chaque ligne d'un département et d'une année
           max(CAST(insee_log AS DOUBLE)) AS denominateur
    FROM {{source:ssmsi-delinquance-departementale}}
    WHERE indicateur IN ('Cambriolages de logement')
    GROUP BY ALL
)
SELECT 'departement' AS maille, d.dep AS code, c.LIBELLE AS libelle, d.annee AS periode,
       round(1000 * d.nombre / d.denominateur, 2) AS valeur
FROM d JOIN {{source:insee-cog-departements}} AS c ON d.dep = c.DEP
UNION ALL
SELECT 'france', 'FR', 'France', annee, round(1000 * sum(nombre) / sum(denominateur), 2)
FROM d
GROUP BY annee
