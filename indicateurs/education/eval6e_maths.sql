-- Évaluations de début de sixième, mathématiques : part des élèves dans les deux groupes de maîtrise les plus faibles.
WITH e AS (
    SELECT CAST(year(annee) AS VARCHAR) AS periode, code_departement, libelle_departement, groupe_1 + groupe_2 AS valeur
    FROM {{source:depp-evaluations-6e-departements}}
    WHERE discipline = 'Mathématiques' AND caracteristique = 'Ensemble'
)
SELECT 'departement' AS maille, e.code_departement AS code, c.LIBELLE AS libelle, e.periode, round(e.valeur, 1) AS valeur
FROM e JOIN {{source:insee-cog-departements}} AS c ON e.code_departement = c.DEP
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(valeur, 1)
FROM e
WHERE code_departement IS NULL AND libelle_departement = 'NATIONAL'
