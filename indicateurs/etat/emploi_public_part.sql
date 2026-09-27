-- Emploi des administrations publiques en % de l'emploi total (OCDE, Panorama des administrations publiques).
-- Codes pays ramenés à la convention Eurostat ; agrégat UE calculé sur les 25 États membres couverts.
WITH pays(iso3, code, libelle, ue) AS (VALUES
    ('AUT', 'AT', 'Autriche', true), ('BEL', 'BE', 'Belgique', true), ('BGR', 'BG', 'Bulgarie', true),
    ('HRV', 'HR', 'Croatie', true), ('CYP', 'CY', 'Chypre', true), ('CZE', 'CZ', 'Tchéquie', true),
    ('DNK', 'DK', 'Danemark', true), ('EST', 'EE', 'Estonie', true), ('FIN', 'FI', 'Finlande', true),
    ('FRA', 'FR', 'France', true), ('DEU', 'DE', 'Allemagne', true), ('GRC', 'EL', 'Grèce', true),
    ('HUN', 'HU', 'Hongrie', true), ('IRL', 'IE', 'Irlande', true), ('ITA', 'IT', 'Italie', true),
    ('LVA', 'LV', 'Lettonie', true), ('LTU', 'LT', 'Lituanie', true), ('LUX', 'LU', 'Luxembourg', true),
    ('MLT', 'MT', 'Malte', true), ('NLD', 'NL', 'Pays-Bas', true), ('POL', 'PL', 'Pologne', true),
    ('PRT', 'PT', 'Portugal', true), ('ROU', 'RO', 'Roumanie', true), ('SVK', 'SK', 'Slovaquie', true),
    ('SVN', 'SI', 'Slovénie', true), ('ESP', 'ES', 'Espagne', true), ('SWE', 'SE', 'Suède', true),
    ('AUS', 'AU', 'Australie', false), ('CAN', 'CA', 'Canada', false), ('CHE', 'CH', 'Suisse', false),
    ('CHL', 'CL', 'Chili', false), ('COL', 'CO', 'Colombie', false), ('CRI', 'CR', 'Costa Rica', false),
    ('GBR', 'UK', 'Royaume-Uni', false), ('ISL', 'IS', 'Islande', false), ('ISR', 'IL', 'Israël', false),
    ('JPN', 'JP', 'Japon', false), ('KOR', 'KR', 'Corée du Sud', false), ('MEX', 'MX', 'Mexique', false),
    ('NOR', 'NO', 'Norvège', false), ('NZL', 'NZ', 'Nouvelle-Zélande', false), ('TUR', 'TR', 'Turquie', false),
    ('USA', 'US', 'États-Unis', false), ('OECD_REP', 'OCDE', 'Moyenne des pays de l''OCDE', false)
),
o AS (
    SELECT REF_AREA, TIME_PERIOD AS periode,
        max(CASE WHEN UNIT_MEASURE = 'PT_EMP' THEN CAST(OBS_VALUE AS DOUBLE) END) AS part,
        max(CASE WHEN UNIT_MEASURE = 'PS' THEN CAST(OBS_VALUE AS DOUBLE) END) AS personnes
    FROM {{source:ocde-emploi-public}}
    WHERE MEASURE = 'EMPG' AND SECTOR = 'S13' AND OBS_VALUE IS NOT NULL AND OBS_VALUE <> 'NaN'
    GROUP BY ALL
),
v AS (
    SELECT p.code, p.libelle, p.ue, o.periode, o.part, o.personnes
    FROM o JOIN pays AS p ON o.REF_AREA = p.iso3
    WHERE o.part IS NOT NULL
),
ue AS (
    SELECT periode, round(100 * sum(personnes) / sum(personnes * 100 / part), 2) AS valeur
    FROM v WHERE ue AND code NOT IN ('CY', 'MT')
    GROUP BY periode
    HAVING count(personnes) = 25
)
SELECT 'pays' AS maille, code, libelle, periode, part AS valeur FROM v
UNION ALL
SELECT 'pays', 'UE_OCDE', 'Union européenne (25 États membres, hors Chypre et Malte)', periode, valeur FROM ue
UNION ALL
SELECT 'france', 'FR', 'France', periode, part FROM v WHERE code = 'FR'
