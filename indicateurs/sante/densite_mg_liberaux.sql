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
    strftime(annee, '%Y') AS periode,
    densite AS valeur
FROM {{source:ameli-demographie-ps}}
WHERE profession_sante = 'Ensemble des médecins généralistes'
  AND classe_age = 'tout_age'
  AND libelle_sexe = 'tout sexe'
  AND densite IS NOT NULL
