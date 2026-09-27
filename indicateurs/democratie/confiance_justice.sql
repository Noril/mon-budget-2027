-- Part des répondants qui ont « plutôt confiance » dans la justice, le système judiciaire national (Eurobaromètre standard, volume A).
-- Période : semestre de fin du terrain (AAAA-S1 ou AAAA-S2) ; pays à deux lettres et moyenne UE27.
WITH e AS (
    SELECT pays, year(fin_terrain) || '-S' || CASE WHEN month(fin_terrain) <= 6 THEN 1 ELSE 2 END AS periode,
           confiance
    FROM {{source:eurobarometre-standard-confiance}}
    WHERE institution = 'justice' AND confiance IS NOT NULL
      AND (regexp_full_match(pays, '[A-Z]{2}') OR pays = 'EU27_2020')
)
SELECT 'pays' AS maille, pays AS code, CASE WHEN pays = 'EU27_2020' THEN 'Union européenne (27)' ELSE pays END AS libelle,
       periode, round(100 * confiance, 0) AS valeur
FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(100 * confiance, 0) FROM e WHERE pays = 'FR'
