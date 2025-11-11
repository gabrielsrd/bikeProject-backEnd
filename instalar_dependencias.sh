#!/bin/bash
################################################################################
# Script de Instalação de Dependências
# 
# Instala todas as dependências necessárias para o processamento completo
################################################################################

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "================================================================================"
echo -e "${BLUE}🔧 INSTALAÇÃO DE DEPENDÊNCIAS${NC}"
echo "================================================================================"
echo ""

# Verificar se pip3 está instalado
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 não encontrado!${NC}"
    echo ""
    echo "Instale o pip3 primeiro:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3-pip"
    exit 1
fi

echo -e "${YELLOW}Verificando dependências atuais...${NC}"
echo ""

# Lista de dependências
DEPS=("pandas" "openpyxl" "django" "tqdm")
MISSING=()
INSTALLED=()

for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        VERSION=$(python3 -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "?")
        echo -e "  ${GREEN}✓${NC} $dep ($VERSION)"
        INSTALLED+=("$dep")
    else
        echo -e "  ${RED}✗${NC} $dep (não instalado)"
        MISSING+=("$dep")
    fi
done

echo ""

# Se tudo estiver instalado
if [ ${#MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Todas as dependências já estão instaladas!${NC}"
    echo ""
    exit 0
fi

# Instalar dependências faltando
echo -e "${YELLOW}Dependências a instalar: ${MISSING[@]}${NC}"
echo ""

read -p "Deseja instalar agora? [S/n]: " response
case "$response" in
    [nN][aA][oO]|[nN])
        echo "Instalação cancelada"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Instalando dependências...${NC}"
echo ""

# Tentar com --user primeiro (não requer sudo)
echo -e "${YELLOW}Tentando instalação sem sudo (--user)...${NC}"
pip3 install --user pandas openpyxl django tqdm

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Instalação concluída com sucesso!${NC}"
    echo ""
    
    # Verificar novamente
    echo "Verificando instalação..."
    ALL_OK=true
    for dep in "${DEPS[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            VERSION=$(python3 -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "?")
            echo -e "  ${GREEN}✓${NC} $dep ($VERSION)"
        else
            echo -e "  ${RED}✗${NC} $dep (falhou)"
            ALL_OK=false
        fi
    done
    
    echo ""
    
    if [ "$ALL_OK" = true ]; then
        echo -e "${GREEN}✅ TUDO PRONTO!${NC}"
        echo ""
        echo "Agora você pode executar:"
        echo -e "${YELLOW}  ./processar_dataset_completo.sh${NC}"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Algumas dependências podem não ter sido instaladas corretamente${NC}"
        echo ""
        echo "Tente instalar manualmente:"
        echo "  pip3 install --user pandas openpyxl django tqdm"
        echo ""
        echo "OU com sudo (se tiver permissão):"
        echo "  sudo pip3 install pandas openpyxl django tqdm"
        echo ""
    fi
else
    echo ""
    echo -e "${RED}❌ Instalação falhou!${NC}"
    echo ""
    echo "Tente manualmente:"
    echo -e "${YELLOW}  pip3 install --user pandas openpyxl django tqdm${NC}"
    echo ""
    echo "OU com sudo (se tiver permissão):"
    echo -e "${YELLOW}  sudo pip3 install pandas openpyxl django tqdm${NC}"
    echo ""
    exit 1
fi
