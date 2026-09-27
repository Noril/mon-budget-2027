-- Dépenses de défense « core » au sens de l'OTAN, en % du PIB (prix de 2021) : tableau 3, bloc « Share of real GDP (%) ».
WITH codes(pays, code) AS (VALUES
    ('Albania', 'AL'), ('Belgium', 'BE'), ('Bulgaria', 'BG'), ('Canada', 'CA'), ('Croatia', 'HR'), ('Czechia', 'CZ'),
    ('Denmark', 'DK'), ('Estonia', 'EE'), ('Finland', 'FI'), ('France', 'FR'), ('Germany', 'DE'), ('Greece', 'EL'),
    ('Hungary', 'HU'), ('Iceland', 'IS'), ('Italy', 'IT'), ('Latvia', 'LV'), ('Lithuania', 'LT'), ('Luxembourg', 'LU'),
    ('Montenegro', 'ME'), ('Netherlands', 'NL'), ('North Macedonia', 'MK'), ('Norway', 'NO'), ('Poland', 'PL'),
    ('Portugal', 'PT'), ('Romania', 'RO'), ('Slovak Republic', 'SK'), ('Slovenia', 'SI'), ('Spain', 'ES'),
    ('Sweden', 'SE'), ('Türkiye', 'TR'), ('United Kingdom', 'UK'), ('United States', 'US'),
    ('NATO Europe and Canada', 'OTAN_EUR_CA'), ('NATO Total', 'OTAN')
),
v AS (
    SELECT c.code, o.pays AS libelle, CAST(o.annee AS VARCHAR) AS periode, o.valeur
    FROM {{source:otan-depenses-defense}} o JOIN codes c USING (pays)
    WHERE o.tableau = 'Table 3' AND o.bloc = 'Share of real GDP (%)'
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
