-- Part de chaque pays dans la puissance de calcul cumulée (Rmax) des 500 supercalculateurs du TOP500.
-- Pays du TOP500 (noms anglais) -> codes Eurostat ; EU27_2020 = somme des 27 États membres.
WITH pays(nom, code, libelle, ue) AS (
    VALUES
        ('Austria', 'AT', 'Autriche', true), ('Belgium', 'BE', 'Belgique', true), ('Bulgaria', 'BG', 'Bulgarie', true),
        ('Croatia', 'HR', 'Croatie', true), ('Cyprus', 'CY', 'Chypre', true), ('Czechia', 'CZ', 'Tchéquie', true),
        ('Czech Republic', 'CZ', 'Tchéquie', true), ('Denmark', 'DK', 'Danemark', true), ('Estonia', 'EE', 'Estonie', true),
        ('Finland', 'FI', 'Finlande', true), ('France', 'FR', 'France', true), ('Germany', 'DE', 'Allemagne', true),
        ('Greece', 'EL', 'Grèce', true), ('Hungary', 'HU', 'Hongrie', true), ('Ireland', 'IE', 'Irlande', true),
        ('Italy', 'IT', 'Italie', true), ('Latvia', 'LV', 'Lettonie', true), ('Lithuania', 'LT', 'Lituanie', true),
        ('Luxembourg', 'LU', 'Luxembourg', true), ('Malta', 'MT', 'Malte', true), ('Netherlands', 'NL', 'Pays-Bas', true),
        ('Poland', 'PL', 'Pologne', true), ('Portugal', 'PT', 'Portugal', true), ('Romania', 'RO', 'Roumanie', true),
        ('Slovakia', 'SK', 'Slovaquie', true), ('Slovenia', 'SI', 'Slovénie', true), ('Spain', 'ES', 'Espagne', true),
        ('Sweden', 'SE', 'Suède', true),
        ('United States', 'US', 'États-Unis', false), ('China', 'CN', 'Chine', false), ('Japan', 'JP', 'Japon', false),
        ('United Kingdom', 'UK', 'Royaume-Uni', false), ('South Korea', 'KR', 'Corée du Sud', false),
        ('Switzerland', 'CH', 'Suisse', false), ('Norway', 'NO', 'Norvège', false)
),
t AS (
    SELECT l.liste, l.rmax_tflops, p.code, p.libelle, p.ue,
           sum(l.rmax_tflops) OVER (PARTITION BY l.liste) AS total
    FROM {{source:top500-listes}} AS l
    LEFT JOIN pays AS p ON l.pays = p.nom
),
v AS (
    SELECT code, libelle, liste AS periode, 100 * sum(rmax_tflops) / any_value(total) AS valeur
    FROM t WHERE code IS NOT NULL GROUP BY code, libelle, liste
    UNION ALL
    SELECT 'EU27_2020', 'Union européenne (27 pays)', liste, 100 * sum(rmax_tflops) / any_value(total)
    FROM t WHERE ue GROUP BY liste
)
SELECT 'pays' AS maille, code, libelle, periode, round(valeur, 2) AS valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, round(valeur, 2) FROM v WHERE code = 'FR'
