-- Prix de l'électricité pour les ménages, tranche DC (2 500 à 4 999 kWh/an), toutes taxes comprises, c€/kWh (Eurostat).
WITH v AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, round(100 * CAST(OBS_VALUE AS DOUBLE), 2) AS valeur
    FROM {{source:eurostat-nrg-pc-204}}
    WHERE split_part(nrg_cons, ':', 1) = 'KWH2500-4999'
      AND split_part(tax, ':', 1) = 'I_TAX'
      AND split_part(currency, ':', 1) = 'EUR'
      AND split_part(unit, ':', 1) = 'KWH' AND OBS_VALUE IS NOT NULL
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
