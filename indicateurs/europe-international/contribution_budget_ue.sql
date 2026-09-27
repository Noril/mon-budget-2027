-- Contributions nationales au budget de l'UE (hors droits de douane), en millions d'euros (Commission, EU spending and revenue).
WITH v AS (
    SELECT pays AS code, pays AS libelle, CAST(annee AS VARCHAR) AS periode, valeur
    FROM {{source:ce-budget-ue-depenses-recettes}}
    WHERE lower(libelle) IN ('total national contribution', 'total national contributions')
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
