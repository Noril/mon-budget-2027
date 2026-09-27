-- Délai médian entre le premier dépôt du texte et la promulgation, en jours, par année de promulgation.
-- Même champ que democratie.lois_promulguees (hors accords internationaux, années complètes depuis 2018).
WITH lois AS (
    SELECT code_loi,
           min(CAST(left(code_loi, 4) AS INTEGER)) AS annee,
           min(CAST(date_promulgation AS DATE)) AS promulgation,
           min(CAST(date_premier_depot AS DATE)) AS depot
    FROM {{source:an-dossiers-legislatifs}}
    WHERE code_loi IS NOT NULL AND NOT (titre_loi ILIKE 'autorisant %')
      -- une date de promulgation mal saisie (0021-02-24 pour la loi 2021-191) est écartée
      AND left(date_promulgation, 4) = left(code_loi, 4)
    GROUP BY code_loi
)
SELECT 'france' AS maille, 'FR' AS code, 'France' AS libelle, CAST(annee AS VARCHAR) AS periode,
       CAST(median(promulgation - depot) AS DOUBLE) AS valeur
FROM lois
WHERE annee >= 2018 AND annee < (SELECT max(annee) FROM lois) AND depot IS NOT NULL
GROUP BY annee
