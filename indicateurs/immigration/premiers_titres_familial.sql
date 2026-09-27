-- Premiers titres de séjour délivrés pour motif familial (DGEF), France entière, par année de délivrance.
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, annee_fichier AS periode,
       CAST(nb_titres AS DOUBLE) AS valeur
FROM {{source:dgef-premiers-titres-motif}}
WHERE motif_principal = 'B. FAMILIAL' AND sous_motif = 'TOTAL'
