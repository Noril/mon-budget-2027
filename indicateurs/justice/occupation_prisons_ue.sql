-- Taux d'occupation des prisons (détenus / capacité officielle), pays européens, Eurostat crim_pris_cap.
-- Agrégat EU27_2020 calculé ici (Eurostat n'en publie pas) : seulement les années où les 27 États membres déclarent les deux séries.
WITH e AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle, TIME_PERIOD AS periode,
           max(CASE WHEN split_part(indic_cr, ':', 1) = 'PRIS_ACT_CAP' THEN CAST(OBS_VALUE AS DOUBLE) END) AS detenus,
           max(CASE WHEN split_part(indic_cr, ':', 1) = 'PRIS_OFF_CAP' THEN CAST(OBS_VALUE AS DOUBLE) END) AS capacite
    FROM {{source:eurostat-crim-pris-cap}}
    WHERE split_part(unit, ':', 1) = 'NR'
    GROUP BY ALL
),
v AS (SELECT * FROM e WHERE detenus IS NOT NULL AND capacite > 0),
ue AS (
    SELECT 'EU27_2020' AS code, 'Union européenne - 27 pays (à partir de 2020)' AS libelle, periode,
           100 * sum(detenus) / sum(capacite) AS valeur
    FROM v
    WHERE code IN ('AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU', 'IE', 'IT',
                   'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK')
    GROUP BY periode
    HAVING count(*) = 27
)
SELECT 'pays' AS maille, code, libelle, periode, round(100 * detenus / capacite, 1) AS valeur FROM v
UNION ALL
SELECT 'pays', code, libelle, periode, round(valeur, 1) FROM ue
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(100 * detenus / capacite, 1) FROM v WHERE code = 'FR'
