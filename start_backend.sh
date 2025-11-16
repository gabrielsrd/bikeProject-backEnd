#!/bin/bash

echo "🚀 Iniciando Backend BikeScience..."
echo ""

# Ativar virtualenv
if [ -d "venv" ]; then
    echo "✓ Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠ Ambiente virtual não encontrado!"
    echo "  Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "  Instalando dependências..."
    pip install -r requirements.txt
fi

echo ""
echo "✓ Verificando instalação do Django..."
python3 -c "import django; print(f'  Django version: {django.get_version()}')" || {
    echo "⚠ Django não instalado. Instalando..."
    pip install django djangorestframework
}

echo ""
echo "✓ Verificando sintaxe do código..."
python3 manage.py check || {
    echo "❌ Erro ao verificar o código!"
    exit 1
}

echo ""
echo "✅ Tudo pronto! Iniciando servidor..."
echo ""
python3 manage.py runserver
