#!/bin/bash
#
# Script para executar todas as análises da monografia
# Autor: Gabriel da Silva Alves
# Data: Novembro 2025
#

set -e  # Parar em caso de erro

echo "=========================================="
echo "  BIKESCIENCE USP - ANÁLISES MONOGRAFIA"
echo "=========================================="
echo ""
echo "Iniciando processamento de todas as análises..."
echo "Este processo pode levar alguns minutos."
echo ""

# Definir diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Criar diretório de resultados
mkdir -p analises_monografia/resultados/graficos

echo ""
echo "=========================================="
echo "  [1/5] Verificação de Dados"
echo "=========================================="
python3 analises_monografia/01_verificar_dados.py

echo ""
echo "=========================================="
echo "  [2/5] Análise Temporal"
echo "=========================================="
python3 analises_monografia/02_analise_temporal.py

echo ""
echo "=========================================="
echo "  [3/5] Análise por Estação"
echo "=========================================="
python3 analises_monografia/03_analise_por_estacao.py

echo ""
echo "=========================================="
echo "  [4/5] Análise de Fluxos"
echo "=========================================="
python3 analises_monografia/04_analise_fluxos.py

echo ""
echo "=========================================="
echo "  [5/5] Geração de Relatório Final"
echo "=========================================="
python3 analises_monografia/05_gerar_relatorio.py

echo ""
echo "=========================================="
echo "  ✅ TODAS AS ANÁLISES CONCLUÍDAS!"
echo "=========================================="
echo ""
echo "📁 Resultados salvos em:"
echo "   • Gráficos: analises_monografia/resultados/graficos/"
echo "   • CSVs: analises_monografia/resultados/"
echo "   • LaTeX: analises_monografia/resultados/estatisticas_monografia.tex"
echo "   • Relatório: analises_monografia/resultados/relatorio_completo.txt"
echo ""
echo "📖 Próximos passos:"
echo "   1. Revisar os gráficos gerados"
echo "   2. Copiar gráficos desejados para monografia/figuras/"
echo "   3. Incluir estatisticas_monografia.tex no preâmbulo do LaTeX"
echo "   4. Usar os comandos \\newcommand no texto da monografia"
echo ""
echo "✨ Pronto para enriquecer sua monografia!"
echo ""
