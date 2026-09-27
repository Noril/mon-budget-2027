-- Participation au premier tour de l'élection présidentielle : votants / inscrits, en %.
-- France : toutes les lignes (départements, outre-mer, Français de l'étranger) ; département : codes du COG.
WITH r AS (
    SELECT annee, code_departement, inscrits, votants
    FROM {{source:interieur-presidentielle-departements}}
    WHERE scrutin = 'presidentielle' AND tour = 1
)
SELECT 'departement' AS maille, r.code_departement AS code, d.LIBELLE AS libelle, CAST(r.annee AS VARCHAR) AS periode,
       round(100 * r.votants / r.inscrits, 2) AS valeur
FROM r JOIN {{source:insee-cog-departements}} AS d ON r.code_departement = d.DEP
UNION ALL
SELECT 'france', 'FR', 'France (y compris Français de l''étranger)', CAST(annee AS VARCHAR),
       round(100 * sum(votants) / sum(inscrits), 2)
FROM r
GROUP BY annee
