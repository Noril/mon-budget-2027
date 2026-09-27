-- Prix de l'électricité pour les entreprises, tranche IC (500 à 1 999 MWh/an), hors TVA et taxes récupérables, c€/kWh (Eurostat).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, round(100 * CAST(OBS_VALUE AS DOUBLE), 2) AS valeur
    FROM {{source:eurostat-nrg-pc-205}}
    WHERE split_part(nrg_cons, ':', 1) = 'MWH500-1999'
      AND split_part(tax, ':', 1) = 'X_VAT'
      AND split_part(currency, ':', 1) = 'EUR'
      AND split_part(unit, ':', 1) = 'KWH' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
