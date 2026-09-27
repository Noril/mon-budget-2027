-- Retours effectifs (migr_eirtn) rapportés aux décisions d'éloignement (migr_eiord) de la même année, en %.
WITH o AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           CAST(OBS_VALUE AS DOUBLE) AS decisions
    FROM {{source:eurostat-migr-eiord}}
    WHERE split_part(citizen, ':', 1) = 'TOTAL' AND split_part(age, ':', 1) = 'TOTAL' AND split_part(sex, ':', 1) = 'T'
      AND split_part(unit, ':', 1) = 'PER' AND OBS_VALUE IS NOT NULL
),
r AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS retours
    FROM {{source:eurostat-migr-eirtn}}
    WHERE split_part(citizen, ':', 1) = 'TOTAL' AND split_part(c_dest, ':', 1) = 'TOTAL' AND split_part(age, ':', 1) = 'TOTAL'
      AND split_part(sex, ':', 1) = 'T' AND split_part(unit, ':', 1) = 'PER' AND OBS_VALUE IS NOT NULL
),
v AS (SELECT o.code, o.libelle, o.periode, round(100 * r.retours / o.decisions, 1) AS valeur
      FROM o JOIN r USING (code, periode) WHERE o.decisions > 0)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
