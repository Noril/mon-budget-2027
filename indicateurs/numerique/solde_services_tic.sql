-- Solde des échanges de services TIC (poste SI de la balance des paiements) avec le reste du monde, en milliards d'euros.
-- Pays : partenaire WRL_REST (reste du monde) ; agrégat EU27_2020 : partenaire EXT_EU27_2020 (hors UE),
-- car son WRL_REST additionne les échanges entre États membres.
WITH e AS (
    SELECT
        split_part(geo, ':', 1) AS code,
        substr(geo, strpos(geo, ':') + 1) AS libelle,
        TIME_PERIOD AS periode,
        CAST(OBS_VALUE AS DOUBLE) / 1000 AS valeur
    FROM {{source:eurostat-bop-its6-det}}
    WHERE split_part(currency, ':', 1) = 'MIO_EUR'
      AND split_part(bop_item, ':', 1) = 'SI'
      AND split_part(stk_flow, ':', 1) = 'BAL'
      AND split_part(partner, ':', 1) = CASE WHEN split_part(geo, ':', 1) = 'EU27_2020' THEN 'EXT_EU27_2020' ELSE 'WRL_REST' END
      AND nullif(OBS_VALUE, '') IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM e
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM e WHERE code = 'FR'
