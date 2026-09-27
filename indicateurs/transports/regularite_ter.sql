-- Régularité des TER : 100 × (1 - trains en retard à l'arrivée / trains ayant circulé), en % (SNCF Voyageurs).
-- Anciennes régions et lots d'exploitation rattachés à la région actuelle (code COG) ; région publiée à partir de 2018,
-- première année où SNCF publie sous les noms des treize régions. Années de douze mois seulement.
WITH correspondance(nom, reg) AS (VALUES
    ('Auvergne-Rhône-Alpes', '84'), ('Rhône Alpes', '84'), ('Auvergne', '84'),
    ('Bourgogne-Franche-Comté', '27'), ('Bourgogne', '27'), ('Franche Comté', '27'),
    ('Bretagne', '53'),
    ('Centre Val-de-Loire', '24'), ('Centre', '24'),
    ('Grand Est', '44'), ('Alsace', '44'), ('Lorraine', '44'), ('Champagne Ardenne', '44'),
    ('Hauts-de-France', '32'), ('Nord Pas de Calais', '32'), ('Picardie', '32'), ('Etoile Amiens', '32'),
    ('Normandie', '28'), ('Haute Normandie', '28'), ('Basse Normandie', '28'),
    ('Nouvelle Aquitaine', '75'), ('Aquitaine', '75'), ('Limousin', '75'), ('Poitou Charentes', '75'),
    ('Occitanie', '76'), ('Midi Pyrénées', '76'), ('Languedoc Roussillon', '76'),
    ('Pays-de-la-Loire', '52'), ('Loire Océan', '52'),
    ('Provence Alpes Côte d''Azur', '93'), ('Sud Azur', '93')
),
t AS (
    SELECT year(t.date) AS annee, month(t.date) AS mois, c.reg,
           t.nombre_de_trains_programmes AS programmes, t.nombre_de_trains_ayant_circule AS circules,
           t.nombre_de_trains_annules AS annules, t.nombre_de_trains_en_retard_a_l_arrivee AS retards
    FROM {{source:sncf-regularite-ter}} AS t LEFT JOIN correspondance AS c ON t.region = c.nom
    WHERE t.nombre_de_trains_en_retard_a_l_arrivee IS NOT NULL
)
SELECT 'region' AS maille, t.reg AS code, r.LIBELLE AS libelle, CAST(t.annee AS VARCHAR) AS periode,
       round(100 * (1 - sum(retards) / sum(circules)), 2) AS valeur
FROM t JOIN {{source:insee-cog-regions}} AS r ON t.reg = r.REG
WHERE t.annee >= 2018
GROUP BY t.reg, r.LIBELLE, t.annee
HAVING count(DISTINCT t.mois) = 12
UNION ALL
SELECT 'france', 'FR', 'France (TER, hors Île-de-France et Corse)', CAST(annee AS VARCHAR), round(100 * (1 - sum(retards) / sum(circules)), 2)
FROM t
GROUP BY annee
HAVING count(DISTINCT mois) = 12
