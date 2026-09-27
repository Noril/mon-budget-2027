-- Lois promulguées par année, hors lois autorisant la ratification ou l'approbation d'un accord international.
-- Une loi = un code_loi distinct (« 2024-42 ») ; année = les quatre premiers caractères du code.
-- Années complètes seulement : de 2018 (XVe législature entière) à l'année précédant la dernière promulgation.
WITH lois AS (
    SELECT code_loi, min(CAST(left(code_loi, 4) AS INTEGER)) AS annee
    FROM {{source:an-dossiers-legislatifs}}
    WHERE code_loi IS NOT NULL AND NOT (titre_loi ILIKE 'autorisant %')
    GROUP BY code_loi
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, CAST(annee AS VARCHAR) AS periode,
       CAST(count(*) AS DOUBLE) AS valeur
FROM lois
WHERE annee >= 2018 AND annee < (SELECT max(annee) FROM lois)
GROUP BY annee
