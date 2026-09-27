-- Sortie attendue de toute formule : maille, code, libelle, periode, valeur
-- {{source:<id>}} est remplacé par la table Parquet normalisée de la source.
SELECT
    CASE
        WHEN region = '99' THEN 'france'
        WHEN departement = '999' THEN 'region'
        ELSE 'departement'
    END AS maille,
    CASE
        WHEN region = '99' THEN 'FR'
        WHEN departement = '999' THEN region
        ELSE departement
    END AS code,
    CASE
        WHEN region = '99' THEN 'France'
        WHEN departement = '999' THEN libelle_region
        ELSE libelle_departement
    END AS libelle,
    CAST(annee AS VARCHAR) AS periode,
    round(taux_patients_ald_sans_mt_integer, 1) AS valeur
FROM {{source:ameli-ald-sans-mt}}
WHERE taux_patients_ald_sans_mt_integer IS NOT NULL
  AND region <> 'inconnu'
