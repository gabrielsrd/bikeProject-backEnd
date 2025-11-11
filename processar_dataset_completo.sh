#!/bin/bash
################################################################################
# Script Master - Processamento COMPLETO do Dataset Tembici
# 
# Executa as 3 etapas:
#   1. Consolidação dos ZIPs → CSV completo
#   2. Importação CSV → SQLite completo
#   3. Verificação e comparação
#
# Uso: ./processar_dataset_completo.sh [opcoes]
#   --consolidar-apenas    : Apenas ETAPA 1
#   --importar-apenas      : Apenas ETAPA 2 (requer CSV completo)
#   --verificar-apenas     : Apenas ETAPA 3
#   --auto                 : Modo automático (sem confirmações)
################################################################################

set -e  # Sair em caso de erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo ""
echo "================================================================================"
echo -e "${BLUE}🚴 PROCESSAMENTO COMPLETO DO DATASET TEMBICI (2018-2023)${NC}"
echo "================================================================================"
echo "Data: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"
echo ""

# Diretório base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Ativar venv se existir
if [ -f "$BASE_DIR/venv/bin/activate" ]; then
    echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
    source "$BASE_DIR/venv/bin/activate"
    echo -e "${GREEN}✓ Venv ativado${NC}"
    echo ""
elif [ -f "$BASE_DIR/.venv/bin/activate" ]; then
    echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
    source "$BASE_DIR/.venv/bin/activate"
    echo -e "${GREEN}✓ Venv ativado${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado${NC}"
    echo "   Certifique-se de ativar manualmente se necessário:"
    echo "   source venv/bin/activate"
    echo ""
fi

# Arquivos
CSV_COMPLETO="$BASE_DIR/dataRaw/consolidated_tembici_data_COMPLETO.csv"
DB_COMPLETO="$BASE_DIR/db_COMPLETO.sqlite3"

# Opções
CONSOLIDAR=true
IMPORTAR=true
VERIFICAR=true
AUTO_MODE=false

# Parse argumentos
for arg in "$@"; do
    case $arg in
        --consolidar-apenas)
            IMPORTAR=false
            VERIFICAR=false
            ;;
        --importar-apenas)
            CONSOLIDAR=false
            VERIFICAR=false
            ;;
        --verificar-apenas)
            CONSOLIDAR=false
            IMPORTAR=false
            ;;
        --auto)
            AUTO_MODE=true
            ;;
    esac
done

# Função de confirmação
confirm() {
    if [ "$AUTO_MODE" = true ]; then
        return 0
    fi
    
    read -p "$1 [S/n]: " response
    case "$response" in
        [nN][aA][oO]|[nN])
            return 1
            ;;
        *)
            return 0
            ;;
    esac
}

# Verificar dependências
echo -e "${YELLOW}Verificando dependências...${NC}"
MISSING_DEPS=""

# Verificar cada dependência individualmente
python3 -c "import pandas" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS} pandas"
python3 -c "import openpyxl" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS} openpyxl"
python3 -c "import django" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS} django"
python3 -c "import tqdm" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS} tqdm"

if [ -n "$MISSING_DEPS" ]; then
    echo -e "${RED}❌ Dependências faltando:${MISSING_DEPS}${NC}"
    echo ""
    echo "Instale com:"
    echo -e "${YELLOW}  pip3 install pandas openpyxl django tqdm${NC}"
    echo ""
    echo "OU execute:"
    echo -e "${YELLOW}  ./instalar_dependencias.sh${NC}"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Dependências OK${NC}"
echo ""

# ============================================================================
# ETAPA 1: CONSOLIDAÇÃO
# ============================================================================

if [ "$CONSOLIDAR" = true ]; then
    echo "================================================================================"
    echo -e "${BLUE}ETAPA 1: CONSOLIDAÇÃO (ZIPs → CSV Completo)${NC}"
    echo "================================================================================"
    echo ""
    
    # Verificar se já existe
    if [ -f "$CSV_COMPLETO" ]; then
        SIZE_MB=$(du -m "$CSV_COMPLETO" | cut -f1)
        LINES=$(wc -l < "$CSV_COMPLETO")
        echo -e "${YELLOW}⚠️  CSV completo já existe!${NC}"
        echo "   Caminho: $CSV_COMPLETO"
        echo "   Tamanho: ${SIZE_MB} MB"
        echo "   Linhas:  $((LINES - 1))"
        echo ""
        
        if ! confirm "Deseja SOBRESCREVER e reprocessar tudo?"; then
            echo -e "${YELLOW}Pulando ETAPA 1 (usando CSV existente)${NC}"
            echo ""
        else
            echo -e "${YELLOW}Removendo CSV antigo...${NC}"
            rm -f "$CSV_COMPLETO"
            
            echo ""
            echo -e "${GREEN}Iniciando consolidação...${NC}"
            echo "Tempo estimado: 30-60 minutos"
            echo ""
            
            python3 scripts/consolidate_tembici_COMPLETO.py
            
            if [ $? -eq 0 ]; then
                echo ""
                echo -e "${GREEN}✅ ETAPA 1 CONCLUÍDA COM SUCESSO!${NC}"
                
                # Estatísticas
                if [ -f "$CSV_COMPLETO" ]; then
                    SIZE_MB=$(du -m "$CSV_COMPLETO" | cut -f1)
                    LINES=$(wc -l < "$CSV_COMPLETO")
                    echo "   CSV gerado: ${SIZE_MB} MB, $((LINES - 1)) viagens"
                fi
            else
                echo ""
                echo -e "${RED}❌ ETAPA 1 FALHOU!${NC}"
                echo "Verifique o log: consolidacao_completa.log"
                exit 1
            fi
        fi
    else
        echo ""
        echo -e "${GREEN}Iniciando consolidação...${NC}"
        echo "Tempo estimado: 30-60 minutos"
        echo ""
        
        python3 scripts/consolidate_tembici_COMPLETO.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✅ ETAPA 1 CONCLUÍDA COM SUCESSO!${NC}"
            
            if [ -f "$CSV_COMPLETO" ]; then
                SIZE_MB=$(du -m "$CSV_COMPLETO" | cut -f1)
                LINES=$(wc -l < "$CSV_COMPLETO")
                echo "   CSV gerado: ${SIZE_MB} MB, $((LINES - 1)) viagens"
            fi
        else
            echo ""
            echo -e "${RED}❌ ETAPA 1 FALHOU!${NC}"
            echo "Verifique o log: consolidacao_completa.log"
            exit 1
        fi
    fi
    
    echo ""
    sleep 2
fi

# ============================================================================
# ETAPA 2: IMPORTAÇÃO
# ============================================================================

if [ "$IMPORTAR" = true ]; then
    echo "================================================================================"
    echo -e "${BLUE}ETAPA 2: IMPORTAÇÃO (CSV → SQLite Completo)${NC}"
    echo "================================================================================"
    echo ""
    
    # Verificar se CSV existe
    if [ ! -f "$CSV_COMPLETO" ]; then
        echo -e "${RED}❌ CSV completo não encontrado: $CSV_COMPLETO${NC}"
        echo "Execute primeiro: ./processar_dataset_completo.sh --consolidar-apenas"
        exit 1
    fi
    
    # Verificar se banco já existe
    if [ -f "$DB_COMPLETO" ]; then
        SIZE_MB=$(du -m "$DB_COMPLETO" | cut -f1)
        echo -e "${YELLOW}⚠️  Banco completo já existe!${NC}"
        echo "   Caminho: $DB_COMPLETO"
        echo "   Tamanho: ${SIZE_MB} MB"
        echo ""
        echo "O script de importação permite:"
        echo "  [1] Continuar importação (se foi interrompida)"
        echo "  [2] Limpar e recomeçar"
        echo "  [3] Cancelar"
        echo ""
    fi
    
    echo -e "${GREEN}Iniciando importação...${NC}"
    echo "Tempo estimado: 60-120 minutos"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Não interrompa (Ctrl+C) sem necessidade!${NC}"
    echo "            Se precisar parar, o progresso será salvo."
    echo ""
    
    if [ "$AUTO_MODE" = false ]; then
        if ! confirm "Iniciar importação agora?"; then
            echo -e "${YELLOW}ETAPA 2 cancelada pelo usuário${NC}"
            VERIFICAR=false
            exit 0
        fi
    fi
    
    python3 scripts/import_to_sqlite_COMPLETO.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ ETAPA 2 CONCLUÍDA COM SUCESSO!${NC}"
        
        if [ -f "$DB_COMPLETO" ]; then
            SIZE_MB=$(du -m "$DB_COMPLETO" | cut -f1)
            echo "   Banco gerado: ${SIZE_MB} MB"
        fi
    else
        echo ""
        echo -e "${YELLOW}⚠️  ETAPA 2 foi interrompida ou teve erro${NC}"
        echo "Verifique o log: importacao_completa.log"
        echo ""
        echo "Para continuar, execute novamente:"
        echo "  ./processar_dataset_completo.sh --importar-apenas"
    fi
    
    echo ""
    sleep 2
fi

# ============================================================================
# ETAPA 3: VERIFICAÇÃO
# ============================================================================

if [ "$VERIFICAR" = true ]; then
    echo "================================================================================"
    echo -e "${BLUE}ETAPA 3: VERIFICAÇÃO E COMPARAÇÃO${NC}"
    echo "================================================================================"
    echo ""
    
    python3 scripts/verificar_dataset_COMPLETO.py
    
    echo ""
fi

# ============================================================================
# FINALIZAÇÃO
# ============================================================================

echo "================================================================================"
echo -e "${GREEN}✅ PROCESSAMENTO FINALIZADO!${NC}"
echo "================================================================================"
echo ""
echo "Arquivos gerados:"

if [ -f "$CSV_COMPLETO" ]; then
    SIZE_MB=$(du -m "$CSV_COMPLETO" | cut -f1)
    LINES=$(wc -l < "$CSV_COMPLETO")
    echo -e "  ${GREEN}✓${NC} CSV completo: ${SIZE_MB} MB, $((LINES - 1)) viagens"
else
    echo -e "  ${YELLOW}⚠${NC} CSV completo: não gerado"
fi

if [ -f "$DB_COMPLETO" ]; then
    SIZE_MB=$(du -m "$DB_COMPLETO" | cut -f1)
    echo -e "  ${GREEN}✓${NC} Banco completo: ${SIZE_MB} MB"
else
    echo -e "  ${YELLOW}⚠${NC} Banco completo: não gerado"
fi

echo ""
echo "Logs disponíveis:"
echo "  • consolidacao_completa.log"
echo "  • importacao_completa.log"

echo ""
echo "Próximos passos:"
echo "  1. Verificar resultados: python3 scripts/verificar_dataset_COMPLETO.py"
echo "  2. Atualizar análises: cd analises_monografia && ./executar_todas_analises.sh"
echo ""
echo "================================================================================"
