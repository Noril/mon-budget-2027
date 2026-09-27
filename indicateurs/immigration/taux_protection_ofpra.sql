-- Taux de protection accordé par l'OFPRA en première instance, en % des décisions OFPRA (réfugié, protection subsidiaire, rejet), clôtures exclues.
WITH o AS (
    SELECT niveau, code_departement, annee_fichier AS annee,
           CAST(refugie AS DOUBLE) + CAST(protection_subsidiaire AS DOUBLE) AS protections,
           CAST(refugie AS DOUBLE) + CAST(protection_subsidiaire AS DOUBLE) + CAST(rejet AS DOUBLE) AS decisions
    FROM {{source:ofpra-decisions-departement}}
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, annee AS periode,
       round(100 * protections / decisions, 1) AS valeur
FROM o WHERE niveau = 'Total' AND decisions > 0
UNION ALL
SELECT 'departement', o.code_departement, d.LIBELLE, o.annee, round(100 * o.protections / o.decisions, 1)
FROM o JOIN {{source:insee-cog-departements}} AS d ON o.code_departement = d.DEP
WHERE o.niveau = 'Département' AND o.decisions > 0
