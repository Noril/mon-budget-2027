-- Solde « dépenses UE reçues − contributions nationales » en % du RNB de l'État membre (Commission, EU spending and revenue).
WITH e AS (
    SELECT
        pays AS code,
        CAST(annee AS VARCHAR) AS periode,
        max(CASE WHEN upper(libelle) = 'TOTAL EXPENDITURE' THEN valeur END) AS depenses,
        max(CASE WHEN lower(libelle) IN ('total national contribution', 'total national contributions') THEN valeur END)
            AS contributions,
        max(CASE WHEN starts_with(libelle, 'Gross National Income (GNI)') THEN valeur END) AS rnb
    FROM {{source:ce-budget-ue-depenses-recettes}}
    GROUP BY ALL
),
v AS (SELECT code, code AS libelle, periode, 100 * (depenses - contributions) / rnb AS valeur FROM e
      WHERE depenses IS NOT NULL AND contributions IS NOT NULL AND rnb IS NOT NULL AND rnb <> 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
