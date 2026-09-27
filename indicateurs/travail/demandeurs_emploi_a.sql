-- Demandeurs d'emploi inscrits à France Travail en catégorie A, moyenne trimestrielle CVS-CJO (DARES).
WITH v AS (
    SELECT date AS periode, code_region, code_departement, CAST(nombre_de_demandeurs_d_emploi AS DOUBLE) AS valeur
    FROM {{source:dares-defm-stock-trim}}
    WHERE type_de_donnees = 'cvs-cjo' AND categorie = 'A' AND sexe = 'Total'
      AND tranche_d_age = 'Total' AND anciennete = 'Total'
      AND nombre_de_demandeurs_d_emploi IS NOT NULL
)
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, periode, valeur
FROM v WHERE code_region = 'Total France' AND code_departement = 'Total'
UNION ALL
SELECT 'region', r.REG, r.LIBELLE, v.periode, v.valeur
FROM v JOIN {{source:insee-cog-regions}} AS r ON v.code_region = r.REG
WHERE v.code_departement = 'Total'
UNION ALL
SELECT 'departement', d.DEP, d.LIBELLE, v.periode, v.valeur
FROM v JOIN {{source:insee-cog-departements}} AS d ON v.code_departement = d.DEP
