#!/bin/bash

# Script de Teste - Efeito Maré
# Execute este script APÓS iniciar o servidor Django

echo "🌊 Testando Implementação do Efeito Maré"
echo "=========================================="
echo ""

# Configuração
BASE_URL="http://localhost:8000"
STATION_ID=244  # Metrô Butantã

echo "📡 Servidor: $BASE_URL"
echo "🚉 Estação de Teste: ID $STATION_ID (Metrô Butantã)"
echo ""

# Teste 1: Endpoint básico
echo "✅ Teste 1: Requisição básica (dias úteis)"
echo "-------------------------------------------"
curl -s "${BASE_URL}/api/station_tide_effect/?station_id=${STATION_ID}" | python3 -m json.tool | head -30
echo ""
echo ""

# Teste 2: Com filtro de dias
echo "✅ Teste 2: Apenas segundas e quartas (dias 0 e 2)"
echo "---------------------------------------------------"
curl -s "${BASE_URL}/api/station_tide_effect/?station_id=${STATION_ID}&days=0,2" | python3 -m json.tool | head -30
echo ""
echo ""

# Teste 3: Excluindo meses de férias
echo "✅ Teste 3: Excluindo janeiro, julho e dezembro"
echo "------------------------------------------------"
curl -s "${BASE_URL}/api/station_tide_effect/?station_id=${STATION_ID}&months=0,6,11" | python3 -m json.tool | head -30
echo ""
echo ""

# Teste 4: Com período específico
echo "✅ Teste 4: Período específico (2020)"
echo "-------------------------------------"
curl -s "${BASE_URL}/api/station_tide_effect/?station_id=${STATION_ID}&startDate=2020-01-01&endDate=2020-12-31" | python3 -m json.tool | head -30
echo ""
echo ""

echo "=========================================="
echo "🎉 Testes Concluídos!"
echo ""
echo "📝 Notas:"
echo "  - Se você viu dados JSON formatados, o backend está funcionando!"
echo "  - Procure por 'balance' nos dados - valores positivos/negativos"
echo "  - total_balance indica o saldo geral da estação"
echo ""
echo "🚀 Próximos Passos:"
echo "  1. Inicie o frontend: cd bikeProject-frontEnd && npm start"
echo "  2. Acesse http://localhost:3000"
echo "  3. Clique na estação Metrô Butantã"
echo "  4. No modal, clique no botão 'Efeito Maré'"
echo ""
