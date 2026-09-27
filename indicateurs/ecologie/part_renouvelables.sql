-- Part des énergies renouvelables dans la consommation finale brute d'énergie (Eurostat, SHARES).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:eurostat-nrg-ind-ren}}
    WHERE split_part(nrg_bal, ':', 1) = 'REN' AND split_part(unit, ':', 1) = 'PC' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
