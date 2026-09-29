-- Contributions nationales au budget de l'UE (hors droits de douane), en millions d'euros (Commission, EU spending and revenue).
-- Ligne explicite jusqu'au fichier 2000-2023 ; depuis le fichier 2000-2025, reconstituée pour 2021 et après :
-- ressources propres − droits de douane − cotisations sucre + soldes et ajustements (identique à la ligne explicite des
-- fichiers précédents, au centime près).
WITH e AS (
    SELECT
        pays AS code,
        CAST(annee AS VARCHAR) AS periode,
        coalesce(
            max(CASE WHEN lower(libelle) IN ('total national contribution', 'total national contributions') THEN valeur END),
            max(CASE WHEN upper(libelle) = 'TOTAL OWN RESOURCES' THEN valeur END)
            - coalesce(max(CASE WHEN starts_with(lower(libelle), 'customs duties') THEN valeur END), 0)
            - coalesce(max(CASE WHEN starts_with(lower(libelle), 'sugar levies') THEN valeur END), 0)
            + max(CASE WHEN upper(libelle) = 'TOTAL BALANCES AND ADJUSTMENTS' THEN valeur END)
        ) AS valeur
    FROM {{source:ce-budget-ue-depenses-recettes}}
    GROUP BY ALL
),
v AS (SELECT code, code AS libelle, periode, valeur FROM e WHERE valeur IS NOT NULL)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
