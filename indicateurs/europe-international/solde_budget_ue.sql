-- Solde « dépenses UE reçues − contributions nationales » par État membre, en millions d'euros (Commission, EU spending and revenue).
WITH e AS (
    SELECT
        pays AS code,
        CAST(annee AS VARCHAR) AS periode,
        max(CASE WHEN upper(libelle) = 'TOTAL EXPENDITURE' THEN valeur END) AS depenses,
        max(CASE WHEN lower(libelle) IN ('total national contribution', 'total national contributions') THEN valeur END)
            AS contributions
    FROM {{source:ce-budget-ue-depenses-recettes}}
    GROUP BY ALL
),
v AS (SELECT code, code AS libelle, periode, depenses - contributions AS valeur FROM e
      WHERE depenses IS NOT NULL AND contributions IS NOT NULL)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
