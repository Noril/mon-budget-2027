-- Solde exportateur des échanges physiques d'électricité en TWh (RTE éCO2mix), positif quand la France exporte (ech_physiques est négatif à l'export).
-- Énergie du mois (MWh) = puissance moyenne du mois (MW) × nombre de jours du mois × 24 ; années de douze mois seulement.
WITH m AS (
    SELECT CAST(annee AS INTEGER) AS annee, CAST(mois AS INTEGER) AS mois,
           CAST(ech_physiques AS DOUBLE) * 24 * day(last_day(make_date(CAST(annee AS INTEGER), CAST(mois AS INTEGER), 1))) AS mwh
    FROM {{source:odre-eco2mix-national}}
    WHERE ech_physiques IS NOT NULL
)
SELECT 'france' AS maille, 'FR' AS code, 'France métropolitaine hors Corse' AS libelle, CAST(annee AS VARCHAR) AS periode,
       round(-sum(mwh) / 1e6, 3) AS valeur
FROM m GROUP BY annee HAVING count(DISTINCT mois) = 12
