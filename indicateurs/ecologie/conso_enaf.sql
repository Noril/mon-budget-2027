-- Consommation d'espaces naturels, agricoles et forestiers (Cerema), en hectares par année.
-- Colonnes nafAAartBB (m²) avec BB = AA + 1 : consommation entre le 1er janvier 20AA et le 1er janvier 20BB.
-- Rattachement commune -> département par le COG 2026, comme pour l'APL : COM et ARM portent DEP ; COMD et COMA
-- le tiennent de leur commune parente ; un code présent en COM et en COMD prend la ligne COM.
WITH cog AS (SELECT * FROM {{source:insee-cog-communes}}),
geo AS (
    SELECT c.COM, coalesce(c.DEP, p.DEP) AS DEP
    FROM cog AS c
    LEFT JOIN cog AS p ON c.COMPARENT = p.COM AND p.TYPECOM IN ('COM', 'ARM')
    QUALIFY row_number() OVER (PARTITION BY c.COM ORDER BY c.TYPECOM IN ('COM', 'ARM') DESC) = 1
),
longue AS (
    UNPIVOT (SELECT idcom, COLUMNS('^naf[0-9]{2}art[0-9]{2}$') FROM {{source:cerema-conso-enaf}})
    ON COLUMNS('^naf[0-9]{2}art[0-9]{2}$') INTO NAME colonne VALUE m2
),
c AS (
    SELECT l.idcom, g.DEP, 2000 + CAST(substr(colonne, 4, 2) AS INTEGER) AS annee, CAST(m2 AS DOUBLE) AS m2
    FROM longue AS l
    LEFT JOIN geo AS g ON l.idcom = g.COM
    WHERE CAST(substr(colonne, 9, 2) AS INTEGER) = CAST(substr(colonne, 4, 2) AS INTEGER) + 1
)
SELECT 'departement' AS maille, c.DEP AS code, d.LIBELLE AS libelle, CAST(c.annee AS VARCHAR) AS periode,
       round(sum(c.m2) / 10000, 1) AS valeur
FROM c JOIN {{source:insee-cog-departements}} AS d ON c.DEP = d.DEP
GROUP BY c.DEP, d.LIBELLE, c.annee
UNION ALL
SELECT 'france', 'FR', 'France hors Mayotte', CAST(annee AS VARCHAR), round(sum(m2) / 10000, 1)
FROM c
GROUP BY annee
