-- ============================================================================
-- SCRIPT DE CORREÇÃO DOS NOMES DAS ESTAÇÕES DA USP
-- Data: 2025-11-16
-- ============================================================================

-- IMPORTANTE: Execute este script após confirmar:
-- 1. Qual é a 18ª estação oficial da USP
-- 2. Se as estações 254, 261 e 262 devem permanecer ou ser removidas

BEGIN TRANSACTION;

-- ============================================================================
-- CORREÇÕES OBRIGATÓRIAS (nomes incorretos)
-- ============================================================================

-- Correção 1: ID 251 - FAU → FEA
-- A estação é da Faculdade de Economia e Administração, não FAU
UPDATE ciclovias_station
SET name = '251 - FEA'
WHERE station_id = 251 AND name = '251 - FAU';

SELECT 'Correção 1: FAU → FEA' as acao, 
       changes() as registros_afetados;

-- Correção 2: ID 253 - Pedalusp Biênio → Biênio POLI
-- Nome oficial deve ser "Biênio POLI"
UPDATE ciclovias_station
SET name = '253 - Biênio POLI'
WHERE station_id = 253 AND name = '253 - Pedalusp Biênio';

SELECT 'Correção 2: Pedalusp Biênio → Biênio POLI' as acao,
       changes() as registros_afetados;

-- ============================================================================
-- VERIFICAÇÕES RECOMENDADAS
-- ============================================================================

-- Listar todas as estações da USP após correções
SELECT 
    station_id as ID,
    name as Nome,
    CASE 
        WHEN station_id IN (243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 255, 256, 257, 258, 259, 260) 
        THEN 'OFICIAL'
        ELSE 'A VERIFICAR'
    END as Status
FROM ciclovias_station
WHERE station_id BETWEEN 242 AND 262
ORDER BY station_id;

-- ============================================================================
-- OPÇÃO: ADICIONAR COMENTÁRIO/OBSERVAÇÃO ÀS ESTAÇÕES NÃO CONFIRMADAS
-- ============================================================================

-- Descomente se quiser marcar estações não confirmadas
-- UPDATE ciclovias_station
-- SET name = name || ' (verificar se é oficial)'
-- WHERE station_id IN (242, 254, 261, 262);

-- ============================================================================
-- CONFIRME AS ALTERAÇÕES OU REVERTA
-- ============================================================================

-- Se tudo estiver correto, execute:
-- COMMIT;

-- Se algo estiver errado, execute:
-- ROLLBACK;

-- Por segurança, deixando sem commit automático
SELECT 'IMPORTANTE: Execute COMMIT para confirmar ou ROLLBACK para cancelar' as aviso;
