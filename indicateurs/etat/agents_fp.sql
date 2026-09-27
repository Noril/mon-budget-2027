-- Effectifs de la fonction publique au 31 décembre, hors militaires (INSEE, SIASP, séries TCRED), en nombre d'agents.
WITH e AS (
    SELECT REF_AREA, TIME_PERIOD AS periode, round(1000 * CAST(OBS_VALUE AS DOUBLE), 0) AS effectif
    FROM {{source:insee-effectifs-fonction-publique}}
    WHERE INDICATEUR = 'EFFECTIFS_FP_HMILIT_TOTAL' AND VERSANTS_FP = 'TOT' AND SEXE = '0'
      AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> 'NaN'
)
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, periode, effectif AS valeur
FROM e WHERE REF_AREA = 'FE'
UNION ALL
SELECT 'region', r.REG, r.LIBELLE, e.periode, e.effectif
FROM e JOIN {{source:insee-cog-regions}} AS r ON e.REF_AREA = 'R' || r.REG
UNION ALL
SELECT 'departement', d.DEP, d.LIBELLE, e.periode, e.effectif
FROM e JOIN {{source:insee-cog-departements}} AS d ON e.REF_AREA = 'D' || d.DEP
