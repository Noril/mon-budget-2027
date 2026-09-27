-- Premières demandes d'asile déposées à l'OFPRA (mineurs accompagnants compris), par département de domiciliation.
WITH o AS (
    SELECT niveau, code_departement, annee_fichier AS annee, CAST(premiere_demande AS DOUBLE) AS valeur
    FROM {{source:ofpra-demandes-departement}}
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, annee AS periode, valeur
FROM o WHERE niveau = 'Total'
UNION ALL
SELECT 'departement', o.code_departement, d.LIBELLE, o.annee, o.valeur
FROM o JOIN {{source:insee-cog-departements}} AS d ON o.code_departement = d.DEP
WHERE o.niveau = 'Département'
