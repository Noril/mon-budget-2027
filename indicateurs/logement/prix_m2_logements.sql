-- Prix moyen au m² des ventes de maisons et d'appartements (DVF), par année civile.
-- Moyenne annuelle = moyenne des moyennes mensuelles pondérée par le nombre de ventes du mois.
WITH m AS (
    SELECT
        echelle_geo,
        code_geo,
        CAST(left(annee_mois, 4) AS INTEGER) AS annee,
        annee_mois,
        CAST(nb_ventes_apt_maison AS DOUBLE) AS ventes,
        CAST(moy_prix_m2_apt_maison AS DOUBLE) AS prix
    FROM {{source:dgfip-dvf-statistiques}}
    WHERE echelle_geo IN ('nation', 'departement')
),
annees AS (
    SELECT annee FROM m WHERE echelle_geo = 'nation' GROUP BY annee HAVING count(DISTINCT annee_mois) = 12
),
a AS (
    SELECT echelle_geo, code_geo, annee, sum(ventes * prix) / sum(ventes) AS prix
    FROM m JOIN annees USING (annee)
    WHERE ventes > 0 AND prix IS NOT NULL
    GROUP BY ALL
)
SELECT 'departement' AS maille, a.code_geo AS code, d.LIBELLE AS libelle, CAST(a.annee AS VARCHAR) AS periode,
       round(a.prix, 0) AS valeur
FROM a JOIN {{source:insee-cog-departements}} AS d ON a.code_geo = d.DEP
WHERE a.echelle_geo = 'departement'
UNION ALL
SELECT 'france', 'FR', 'France hors Alsace-Moselle et Mayotte', CAST(annee AS VARCHAR), round(prix, 0)
FROM a
WHERE echelle_geo = 'nation'
