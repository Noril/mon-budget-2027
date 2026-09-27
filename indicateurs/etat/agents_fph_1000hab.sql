-- Agents de la fonction publique hospitalière pour 1 000 habitants (INSEE, SIASP, séries TCRED), rapportés à la population au 1er janvier N+1.
WITH e AS (
    SELECT REF_AREA, CAST(TIME_PERIOD AS INTEGER) AS annee, 1000 * CAST(OBS_VALUE AS DOUBLE) AS effectif
    FROM {{source:insee-effectifs-fonction-publique}}
    WHERE INDICATEUR = 'EFFECTIFS_FP_HOSPITALIERE' AND VERSANTS_FP = 'FPH' AND SEXE = '0'
      AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> 'NaN'
),
p AS (
    SELECT GEO, GEO_OBJECT, CAST(TIME_PERIOD AS INTEGER) AS annee, CAST(OBS_VALUE AS DOUBLE) AS pop
    FROM {{source:insee-estimations-population}}
    WHERE EP_MEASURE = 'POP_JAN_1ST' AND AGE = '_T' AND SEX = '_T'
)
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, CAST(e.annee AS VARCHAR) AS periode,
       round(1000 * e.effectif / p.pop, 2) AS valeur
FROM e JOIN p ON p.GEO = 'F_X_D976' AND p.GEO_OBJECT = 'FRANCE' AND p.annee = e.annee + 1
WHERE e.REF_AREA = 'FE'
UNION ALL
SELECT 'region', r.REG, r.LIBELLE, CAST(e.annee AS VARCHAR), round(1000 * e.effectif / p.pop, 2)
FROM e
JOIN {{source:insee-cog-regions}} AS r ON e.REF_AREA = 'R' || r.REG
JOIN p ON p.GEO_OBJECT = 'REG' AND p.GEO = r.REG AND p.annee = e.annee + 1
UNION ALL
SELECT 'departement', d.DEP, d.LIBELLE, CAST(e.annee AS VARCHAR), round(1000 * e.effectif / p.pop, 2)
FROM e
JOIN {{source:insee-cog-departements}} AS d ON e.REF_AREA = 'D' || d.DEP
JOIN p ON p.GEO_OBJECT = 'DEP' AND p.GEO = d.DEP AND p.annee = e.annee + 1
