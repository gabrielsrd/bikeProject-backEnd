#!/bin/bash
# Script para executar todas as análises do contexto USP
# Autor: Gabriel (TCC - USP)
# Data: Novembro 2025

echo "================================================================================================"
echo "  🚴 ANÁLISES DO CONTEXTO USP - SISTEMA BIKESHARE COMPARTILHADO"
echo "================================================================================================"
echo ""

# Mudar para o diretório do projeto
cd /home/gbiel/gabriel/usp/tcc/bikeProject-backEnd

echo "📂 Diretório de trabalho: $(pwd)"
echo ""

# Verificar se o banco de dados existe
if [ ! -f "db.sqlite3" ]; then
    echo "❌ ERRO: Banco de dados 'db.sqlite3' não encontrado!"
    echo "   Execute primeiro: python manage.py migrate"
    exit 1
fi

echo "✅ Banco de dados encontrado: db.sqlite3"
echo ""

# Criar diretório de resultados se não existir
mkdir -p analises_monografia/resultados

echo "📊 Iniciando análises..."
echo ""

# Executar script master
python3 analises_monografia/EXECUTAR_TODAS_ANALISES.py

# Verificar se executou com sucesso
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================================"
    echo "  ✅ ANÁLISES CONCLUÍDAS COM SUCESSO!"
    echo "================================================================================================"
    echo ""
    echo "📁 Resultados salvos em: analises_monografia/resultados/"
    echo ""
    echo "📊 Arquivos gerados:"
    ls -lh analises_monografia/resultados/*.png 2>/dev/null | wc -l | xargs echo "   - Gráficos PNG:"
    ls -lh analises_monografia/resultados/*.csv 2>/dev/null | wc -l | xargs echo "   - Arquivos CSV:"
    echo ""
    echo "📝 Relatório consolidado:"
    echo "   - RELATORIO_ANALISES_CONTEXTO_USP.md"
    echo ""
    echo "🎓 Próximos passos:"
    echo "   1. Revisar gráficos: cd analises_monografia/resultados && ls *.png"
    echo "   2. Ver relatório: cat analises_monografia/resultados/RELATORIO_ANALISES_CONTEXTO_USP.md"
    echo "   3. Incluir na monografia (Capítulo 5 - Discussão)"
    echo ""
else
    echo ""
    echo "================================================================================================"
    echo "  ❌ ERRO NA EXECUÇÃO!"
    echo "================================================================================================"
    echo ""
    echo "Verifique os logs acima para identificar o problema."
    echo ""
    exit 1
fi
