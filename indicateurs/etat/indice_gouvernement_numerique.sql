-- Indice de gouvernement numérique de l'OCDE (DGI, 0 à 1). Codes pays ramenés à la convention Eurostat ;
-- agrégat UE = moyenne simple des États membres couverts.
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
    ('USA', 'US', 'États-Unis', false), ('ARG', 'AR', 'Argentine', false), ('BRA', 'BR', 'Brésil', false),
    ('IDN', 'ID', 'Indonésie', false), ('PER', 'PE', 'Pérou', false), ('THA', 'TH', 'Thaïlande', false),
    ('OECD_REP', 'OCDE', 'Moyenne des pays de l''OCDE', false)
),
v AS (
    SELECT DISTINCT p.code, p.libelle, p.ue, o.TIME_PERIOD AS periode, CAST(o.OBS_VALUE AS DOUBLE) AS valeur
    FROM {{source:ocde-gouvernement-numerique}} AS o JOIN pays AS p ON o.REF_AREA = p.iso3
    WHERE o.MEASURE = 'DG' AND o.UNIT_MEASURE = 'IX' AND o.OBS_VALUE IS NOT NULL AND o.OBS_VALUE <> 'NaN'
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'pays', 'UE_OCDE', 'Union européenne, moyenne simple des ' || count(*) || ' États membres couverts', periode,
       round(avg(valeur), 3)
FROM v WHERE ue GROUP BY periode
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
