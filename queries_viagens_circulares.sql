-- ═══════════════════════════════════════════════════════════════════════════
-- QUERIES SQL - VIAGENS CIRCULARES CAMPUS USP
-- Use estas queries no DBeaver para análise das viagens circulares
-- ═══════════════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────────────────
-- 1. LISTAR TODAS AS 17 ESTAÇÕES USP
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    id,
    name,
    address
FROM ciclovias_station
WHERE id IN (
    56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
    56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
)
ORDER BY name;


-- ───────────────────────────────────────────────────────────────────────────
-- 2. CONTAR VIAGENS CIRCULARES POR ESTAÇÃO (ranking completo)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    s.id,
    s.name AS estacao,
    COUNT(*) AS viagens_circulares,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(*) 
        FROM ciclovias_trip 
        WHERE initial_station_id = final_station_id
          AND initial_station_id IN (56826,56659,48852,38476,56642,38582,56762,38425,56965,56713,56640,44878,37915,48848,38637,56654,42323)
    ), 2) AS percentual,
    ROUND(AVG(duration_seconds / 60.0), 1) AS duracao_media_min,
    ROUND(MIN(duration_seconds / 60.0), 1) AS duracao_min_min,
    ROUND(MAX(duration_seconds / 60.0), 1) AS duracao_max_min
FROM ciclovias_trip t
JOIN ciclovias_station s ON t.initial_station_id = s.id
WHERE t.initial_station_id = t.final_station_id
  AND t.initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
GROUP BY s.id, s.name
ORDER BY viagens_circulares DESC;


-- ───────────────────────────────────────────────────────────────────────────
-- 3. TOTAL GERAL DE VIAGENS CIRCULARES (resumo)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    COUNT(*) AS total_viagens_circulares,
    ROUND(AVG(duration_seconds / 60.0), 1) AS duracao_media_min,
    ROUND(MIN(duration_seconds / 60.0), 1) AS duracao_min_min,
    ROUND(MAX(duration_seconds / 60.0), 1) AS duracao_max_min
FROM ciclovias_trip
WHERE initial_station_id = final_station_id
  AND initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  );


-- ───────────────────────────────────────────────────────────────────────────
-- 4. VIAGENS CIRCULARES NO BANDEJÃO CENTRAL (ID 38476) - Amostra de 100
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    id,
    initial_station_id,
    final_station_id,
    initial_station_name,
    start_date,
    start_hour,
    ROUND(duration_seconds / 60.0, 1) AS duracao_minutos
FROM ciclovias_trip
WHERE initial_station_id = 38476
  AND final_station_id = 38476
ORDER BY start_date DESC, start_hour
LIMIT 100;


-- ───────────────────────────────────────────────────────────────────────────
-- 5. DISTRIBUIÇÃO POR FAIXAS DE DURAÇÃO
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    CASE 
        WHEN duration_seconds / 60.0 < 5 THEN '1. < 5 min (engano)'
        WHEN duration_seconds / 60.0 < 15 THEN '2. 5-15 min (curta)'
        WHEN duration_seconds / 60.0 < 30 THEN '3. 15-30 min (média)'
        WHEN duration_seconds / 60.0 < 60 THEN '4. 30-60 min (longa)'
        WHEN duration_seconds / 60.0 < 120 THEN '5. 60-120 min (extensa)'
        ELSE '6. >= 120 min (prolongada)'
    END AS faixa_duracao,
    COUNT(*) AS quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual
FROM ciclovias_trip
WHERE initial_station_id = final_station_id
  AND initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
GROUP BY faixa_duracao
ORDER BY faixa_duracao;


-- ───────────────────────────────────────────────────────────────────────────
-- 6. DISTRIBUIÇÃO POR HORÁRIO (0-23h)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    start_hour AS hora,
    COUNT(*) AS viagens,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual
FROM ciclovias_trip
WHERE initial_station_id = final_station_id
  AND initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
GROUP BY start_hour
ORDER BY start_hour;


-- ───────────────────────────────────────────────────────────────────────────
-- 7. COMPARAÇÃO: Circulares vs Não-circulares (viagens internas USP)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    CASE 
        WHEN initial_station_id = final_station_id THEN 'Circular (mesma origem/destino)'
        ELSE 'Não-circular (origem ≠ destino)'
    END AS tipo_viagem,
    COUNT(*) AS quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual,
    ROUND(AVG(duration_seconds / 60.0), 1) AS duracao_media_min
FROM ciclovias_trip
WHERE initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
  AND final_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
GROUP BY tipo_viagem;


-- ───────────────────────────────────────────────────────────────────────────
-- 8. TOP 20 ROTAS CIRCULARES MAIS FREQUENTES (com detalhes)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    s.name AS estacao,
    COUNT(*) AS viagens,
    ROUND(AVG(duration_seconds / 60.0), 1) AS duracao_media_min,
    MIN(start_date) AS primeira_viagem,
    MAX(start_date) AS ultima_viagem,
    COUNT(DISTINCT start_date) AS dias_com_viagens
FROM ciclovias_trip t
JOIN ciclovias_station s ON t.initial_station_id = s.id
WHERE t.initial_station_id = t.final_station_id
  AND t.initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
GROUP BY s.name
ORDER BY viagens DESC
LIMIT 20;


-- ───────────────────────────────────────────────────────────────────────────
-- 9. BANDEJÃO CENTRAL - Distribuição por hora do dia
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    start_hour AS hora,
    COUNT(*) AS viagens_bandejao,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentual
FROM ciclovias_trip
WHERE initial_station_id = 38476  -- Bandejão Central
  AND final_station_id = 38476
GROUP BY start_hour
ORDER BY start_hour;


-- ───────────────────────────────────────────────────────────────────────────
-- 10. EXEMPLOS DE VIAGENS CIRCULARES (amostra variada)
-- ───────────────────────────────────────────────────────────────────────────

SELECT 
    t.id,
    s.name AS estacao,
    t.start_date,
    t.start_hour,
    ROUND(t.duration_seconds / 60.0, 1) AS duracao_min,
    CASE 
        WHEN t.duration_seconds / 60.0 < 5 THEN 'Muito curta'
        WHEN t.duration_seconds / 60.0 < 30 THEN 'Curta'
        WHEN t.duration_seconds / 60.0 < 60 THEN 'Média'
        WHEN t.duration_seconds / 60.0 < 120 THEN 'Longa'
        ELSE 'Muito longa'
    END AS classificacao
FROM ciclovias_trip t
JOIN ciclovias_station s ON t.initial_station_id = s.id
WHERE t.initial_station_id = t.final_station_id
  AND t.initial_station_id IN (
      56826, 56659, 48852, 38476, 56642, 38582, 56762, 38425, 56965,
      56713, 56640, 44878, 37915, 48848, 38637, 56654, 42323
  )
ORDER BY RANDOM()
LIMIT 50;


-- ═══════════════════════════════════════════════════════════════════════════
-- REFERÊNCIA: IDs DAS 17 ESTAÇÕES USP
-- ═══════════════════════════════════════════════════════════════════════════
--
-- 56826 - Letras
-- 56659 - Bancos/Reitoria
-- 48852 - Biblioteca Brasiliana
-- 38476 - Bandejão Central ⭐ (maior número de circulares: 7.353 viagens)
-- 56642 - Bandejão Química
-- 38582 - IME/FAU
-- 56762 - Psicologia
-- 38425 - Biênio Poli USP
-- 56965 - Terminal de Ônibus USP
-- 56713 - Bandejão Prefeitura
-- 56640 - Odontologia
-- 44878 - Portão 1 USP (P1)
-- 37915 - CEPE
-- 48848 - Raia Olímpica USP (P1)
-- 38637 - PORTÃO CPTM
-- 56654 - Hospital Universitário
-- 42323 - Harmonia (P3)
--
-- ═══════════════════════════════════════════════════════════════════════════
-- INFORMAÇÕES ÚTEIS:
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Tabelas:
--   - ciclovias_trip      : Viagens
--   - ciclovias_station   : Estações
--
-- Campos principais em ciclovias_trip:
--   - id                   : ID único da viagem
--   - initial_station_id   : ID da estação de origem
--   - final_station_id     : ID da estação de destino
--   - duration_seconds     : Duração em segundos
--   - start_hour           : Hora de início (0-23)
--   - start_date           : Data da viagem
--   - initial_station_name : Nome da estação de origem
--   - final_station_name   : Nome da estação de destino
--
-- Condição para viagens circulares:
--   WHERE initial_station_id = final_station_id
--
-- ═══════════════════════════════════════════════════════════════════════════
