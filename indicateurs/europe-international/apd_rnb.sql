-- APD en % du RNB (OCDE, CAD) : équivalent-don (MEASURE 11002) à partir de 2018, versements nets (MEASURE 2) avant.
WITH codes(donneur, code) AS (VALUES
    ('ARE', 'AE'), ('AUS', 'AU'), ('AUT', 'AT'), ('AZE', 'AZ'), ('BEL', 'BE'), ('BGR', 'BG'), ('CAN', 'CA'),
    ('CHE', 'CH'), ('CYP', 'CY'), ('CZE', 'CZ'), ('DEU', 'DE'), ('DNK', 'DK'), ('ESP', 'ES'), ('EST', 'EE'),
    ('FIN', 'FI'), ('FRA', 'FR'), ('GBR', 'UK'), ('GRC', 'EL'), ('HRV', 'HR'), ('HUN', 'HU'), ('IRL', 'IE'),
    ('ISL', 'IS'), ('ISR', 'IL'), ('ITA', 'IT'), ('JPN', 'JP'), ('KAZ', 'KZ'), ('KOR', 'KR'), ('KWT', 'KW'),
    ('LIE', 'LI'), ('LTU', 'LT'), ('LUX', 'LU'), ('LVA', 'LV'), ('MCO', 'MC'), ('MLT', 'MT'), ('NLD', 'NL'),
    ('NOR', 'NO'), ('NZL', 'NZ'), ('POL', 'PL'), ('PRT', 'PT'), ('QAT', 'QA'), ('ROU', 'RO'), ('SAU', 'SA'),
    ('SVK', 'SK'), ('SVN', 'SI'), ('SWE', 'SE'), ('THA', 'TH'), ('TUR', 'TR'), ('TWN', 'TW'), ('USA', 'US')
),
o AS (
    SELECT DONOR AS donneur, Donor_1 AS libelle, TIME_PERIOD AS periode, MEASURE AS mesure,
           CAST(OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:ocde-cad-apd-rnb}}
    WHERE UNIT_MEASURE = 'PT_B5G' AND PRICE_BASE = 'V' AND OBS_VALUE IS NOT NULL
      AND ((MEASURE = '11002' AND FLOW_TYPE = '1160' AND CAST(TIME_PERIOD AS INTEGER) >= 2018)
        OR (MEASURE = '2' AND FLOW_TYPE = '1140' AND CAST(TIME_PERIOD AS INTEGER) < 2018))
),
v AS (SELECT coalesce(c.code, o.donneur) AS code, o.libelle, o.periode, o.valeur
      FROM o LEFT JOIN codes c USING (donneur))
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
