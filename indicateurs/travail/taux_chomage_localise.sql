-- Taux de chômage localisé (INSEE, BDM flux TAUX-CHOMAGE), trimestriel CVS. Trimestres recodés AAAA-Tn.
WITH v AS (
    SELECT REF_AREA, replace(TIME_PERIOD, '-Q', '-T') AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:insee-chomage-localise}}
    WHERE INDICATEUR = 'TAUX_CHOMAGE_LOCALISE' AND FREQ = 'T' AND CORRECTION = 'CVS'
      AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> 'NaN'
)
SELECT 'france' AS maille, 'FR' AS code, 'France hors Mayotte' AS libelle, periode, valeur
FROM v WHERE REF_AREA = 'FR-D976'
UNION ALL
SELECT 'region', r.REG, r.LIBELLE, v.periode, v.valeur
FROM v JOIN {{source:insee-cog-regions}} AS r ON v.REF_AREA = 'R' || r.REG
UNION ALL
SELECT 'departement', d.DEP, d.LIBELLE, v.periode, v.valeur
FROM v JOIN {{source:insee-cog-departements}} AS d ON v.REF_AREA = 'D' || d.DEP
