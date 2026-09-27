-- Émissions de gaz à effet de serre par habitant (hors UTCATF et transports internationaux), Eurostat.
WITH ges AS (
    SELECT split_part(geo, ':', 1) AS code, substr(geo, strpos(geo, ':') + 1) AS libelle,
           TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS mio_t
    FROM {{source:eurostat-env-air-gge}}
    WHERE split_part(unit, ':', 1) = 'MIO_T' AND split_part(airpol, ':', 1) = 'GHG'
      AND split_part(src_crf, ':', 1) = 'TOTX4_MEMO' AND OBS_VALUE IS NOT NULL
),
pop AS (
    SELECT split_part(geo, ':', 1) AS code, TIME_PERIOD AS periode, CAST(OBS_VALUE AS DOUBLE) AS pop
    FROM {{source:eurostat-demo-gind}}
    WHERE split_part(indic_de, ':', 1) = 'AVG' AND OBS_VALUE IS NOT NULL
),
v AS (
    SELECT ges.code, ges.libelle, ges.periode, round(1e6 * ges.mio_t / pop.pop, 2) AS valeur
    FROM ges JOIN pop USING (code, periode)
    WHERE pop.pop > 0
)
SELECT 'pays' AS maille, code, libelle, periode, valeur FROM v
UNION ALL
SELECT 'france', 'FR', 'France', periode, valeur FROM v WHERE code = 'FR'
