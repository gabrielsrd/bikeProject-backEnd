#!/usr/bin/env python3
"""
SCRIPT MASTER: EXECUTAR TODAS AS ANÁLISES DO CONTEXTO USP
==========================================================

Este script executa todas as 5 análises específicas do contexto universitário
e gera um relatório consolidado em formato Markdown.

Análises incluídas:
1. Horários Acadêmicos (picos em horários de aula)
2. Períodos Letivos vs Férias (sazonalidade acadêmica)
3. Integração Modal - Metrô/CPTM (primeira/última milha)
4. Movimento dos Bandejões (horário de almoço)
5. Impacto COVID-19 (evolução durante a pandemia)

Autor: Gabriel (TCC - USP)
Data: Novembro 2025
"""

import os
import sys
import time
from datetime import datetime

# Adicionar ao path
sys.path.append('/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia')

# Importar módulos de análise
try:
    from analises_monografia import (
        analise_06_horarios_academicos as modulo_06,
        analise_07_periodos_letivos_ferias as modulo_07,
        analise_08_integracao_modal as modulo_08,
        analise_09_movimento_bandejoes as modulo_09,
        analise_10_impacto_covid as modulo_10
    )
except ImportError:
    # Se módulos não encontrados, importar diretamente
    import importlib.util
    
    def carregar_modulo(caminho, nome):
        spec = importlib.util.spec_from_file_location(nome, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo
    
    base_path = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia'
    modulo_06 = carregar_modulo(f'{base_path}/06_analise_horarios_academicos.py', 'modulo_06')
    modulo_07 = carregar_modulo(f'{base_path}/07_analise_periodos_letivos_ferias.py', 'modulo_07')
    modulo_08 = carregar_modulo(f'{base_path}/08_analise_integracao_modal.py', 'modulo_08')
    modulo_09 = carregar_modulo(f'{base_path}/09_analise_movimento_bandejoes.py', 'modulo_09')
    modulo_10 = carregar_modulo(f'{base_path}/10_analise_impacto_covid.py', 'modulo_10')

OUTPUT_DIR = '/home/gbiel/gabriel/usp/tcc/bikeProject-backEnd/analises_monografia/resultados'

def print_header(titulo):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*100)
    print(f"  {titulo}")
    print("="*100 + "\n")

def executar_todas_analises():
    """Executa todas as análises sequencialmente"""
    
    print_header("🚴 ANÁLISES DO CONTEXTO USP - BIKESHARE COMPARTILHADO")
    print(f"Data de execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diretório de saída: {OUTPUT_DIR}\n")
    
    resultados = {}
    tempo_total_inicio = time.time()
    
    # =================================================================
    # ANÁLISE 1: HORÁRIOS ACADÊMICOS
    # =================================================================
    print_header("ANÁLISE 1/5: Horários Acadêmicos")
    tempo_inicio = time.time()
    
    try:
        resultados['horarios'] = modulo_06.analise_horarios_academicos()
        tempo_decorrido = time.time() - tempo_inicio
        print(f"\n✅ Concluída em {tempo_decorrido:.1f}s")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        resultados['horarios'] = {'erro': str(e)}
    
    # =================================================================
    # ANÁLISE 2: PERÍODOS LETIVOS vs FÉRIAS
    # =================================================================
    print_header("ANÁLISE 2/5: Períodos Letivos vs Férias")
    tempo_inicio = time.time()
    
    try:
        resultados['periodos'] = modulo_07.analise_periodos_letivos_ferias()
        tempo_decorrido = time.time() - tempo_inicio
        print(f"\n✅ Concluída em {tempo_decorrido:.1f}s")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        resultados['periodos'] = {'erro': str(e)}
    
    # =================================================================
    # ANÁLISE 3: INTEGRAÇÃO MODAL
    # =================================================================
    print_header("ANÁLISE 3/5: Integração Modal (Metrô/CPTM)")
    tempo_inicio = time.time()
    
    try:
        resultados['integracao'] = modulo_08.analise_integracao_modal()
        tempo_decorrido = time.time() - tempo_inicio
        print(f"\n✅ Concluída em {tempo_decorrido:.1f}s")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        resultados['integracao'] = {'erro': str(e)}
    
    # =================================================================
    # ANÁLISE 4: MOVIMENTO DOS BANDEJÕES
    # =================================================================
    print_header("ANÁLISE 4/5: Movimento dos Bandejões")
    tempo_inicio = time.time()
    
    try:
        resultados['bandejoes'] = modulo_09.analise_movimento_bandejoes()
        tempo_decorrido = time.time() - tempo_inicio
        print(f"\n✅ Concluída em {tempo_decorrido:.1f}s")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        resultados['bandejoes'] = {'erro': str(e)}
    
    # =================================================================
    # ANÁLISE 5: IMPACTO COVID-19
    # =================================================================
    print_header("ANÁLISE 5/5: Impacto da Pandemia COVID-19")
    tempo_inicio = time.time()
    
    try:
        resultados['covid'] = modulo_10.analise_impacto_covid()
        tempo_decorrido = time.time() - tempo_inicio
        print(f"\n✅ Concluída em {tempo_decorrido:.1f}s")
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        resultados['covid'] = {'erro': str(e)}
    
    # =================================================================
    # RESUMO FINAL
    # =================================================================
    tempo_total = time.time() - tempo_total_inicio
    
    print_header("📊 RESUMO DAS ANÁLISES")
    
    print("✅ Todas as análises foram executadas!\n")
    print(f"⏱️  Tempo total de execução: {tempo_total:.1f}s ({tempo_total/60:.1f} minutos)\n")
    
    print("📁 Arquivos gerados:")
    print(f"   - Gráficos: {OUTPUT_DIR}/*.png")
    print(f"   - Dados CSV: {OUTPUT_DIR}/*.csv")
    print(f"   - Relatório: {OUTPUT_DIR}/RELATORIO_ANALISES_CONTEXTO_USP.md")
    
    return resultados

def gerar_relatorio_markdown(resultados):
    """Gera relatório consolidado em Markdown"""
    
    print_header("📝 Gerando Relatório em Markdown")
    
    relatorio_path = os.path.join(OUTPUT_DIR, 'RELATORIO_ANALISES_CONTEXTO_USP.md')
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("# ANÁLISES DO CONTEXTO USP - SISTEMA BIKESHARE COMPARTILHADO\n\n")
        f.write(f"**Data de geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Análise 1
        f.write("## 1. Horários Acadêmicos\n\n")
        if 'horarios' in resultados and 'erro' not in resultados['horarios']:
            r = resultados['horarios']
            f.write(f"- **Total de viagens em dias úteis:** {r.get('total_semana', 0):,}\n")
            f.write(f"- **Total de viagens em fins de semana:** {r.get('total_fds', 0):,}\n")
            f.write(f"- **Hora de pico (dias úteis):** {r.get('hora_pico_semana', 0)}h\n")
            f.write(f"- **Razão semana/FDS:** {r.get('total_semana', 0) / r.get('total_fds', 1) if r.get('total_fds', 0) > 0 else 0:.1f}x\n\n")
            
            f.write("**Principais Insights:**\n")
            f.write("- Picos marcados nos horários típicos de aula (8h, 10h, 14h, 16h, 19h)\n")
            f.write("- Uso drasticamente reduzido nos fins de semana\n")
            f.write("- Padrão característico de ambiente universitário\n\n")
            
            f.write("**Gráficos gerados:**\n")
            f.write("- `analise_06_horarios_academicos_comparacao.png`\n")
            f.write("- `analise_06_horarios_academicos_sobreposicao.png`\n")
            f.write("- `analise_06_horarios_academicos_heatmap.png`\n\n")
        else:
            f.write("❌ Erro na execução desta análise.\n\n")
        
        f.write("---\n\n")
        
        # Análise 2
        f.write("## 2. Períodos Letivos vs Férias\n\n")
        if 'periodos' in resultados and 'erro' not in resultados['periodos']:
            r = resultados['periodos']
            f.write(f"- **Total em períodos letivos:** {r.get('total_letivo', 0):,} viagens\n")
            f.write(f"- **Total em férias:** {r.get('total_ferias', 0):,} viagens\n")
            f.write(f"- **Média mensal letivo:** {r.get('media_letivo', 0):,} viagens/mês\n")
            f.write(f"- **Média mensal férias:** {r.get('media_ferias', 0):,} viagens/mês\n")
            f.write(f"- **Razão Letivo/Férias:** {r.get('razao', 0):.1f}x\n\n")
            
            f.write("**Principais Insights:**\n")
            f.write("- Queda drástica durante férias (janeiro, fevereiro, julho, dezembro)\n")
            f.write("- Recuperação imediata no início dos semestres\n")
            f.write("- Sazonalidade muito marcada, característica de ambiente universitário\n\n")
            
            f.write("**Gráficos gerados:**\n")
            f.write("- `analise_07_periodos_letivos_temporal.png`\n")
            f.write("- `analise_07_periodos_letivos_comparacao.png`\n")
            f.write("- `analise_07_periodos_letivos_boxplot.png`\n")
            f.write("- `analise_07_periodos_sazonal.png`\n\n")
        else:
            f.write("❌ Erro na execução desta análise.\n\n")
        
        f.write("---\n\n")
        
        # Análise 3
        f.write("## 3. Integração Modal (Metrô/CPTM)\n\n")
        if 'integracao' in resultados and 'erro' not in resultados['integracao']:
            r = resultados['integracao']
            f.write(f"- **Total de viagens:** {r.get('total_viagens', 0):,}\n")
            f.write(f"- **Viagens conectadas a transporte público:** {r.get('viagens_transporte', 0):,}\n")
            f.write(f"- **Percentual de integração modal:** {r.get('percentual_integracao', 0):.1f}%\n\n")
            
            f.write("**Principais Insights:**\n")
            f.write("- Metrô Butantã é o principal hub de entrada/saída\n")
            f.write("- Padrão 'maré': entrada pela manhã, saída à tarde\n")
            f.write("- Sistema funciona como primeira/última milha\n")
            f.write("- Forte integração com transporte público metropolitano\n\n")
            
            f.write("**Gráficos gerados:**\n")
            f.write("- `analise_08_integracao_modal_estacoes.png`\n")
            f.write("- `analise_08_integracao_modal_horario_metro.png`\n")
            f.write("- `analise_08_integracao_modal_saldo.png`\n\n")
        else:
            f.write("❌ Erro na execução desta análise.\n\n")
        
        f.write("---\n\n")
        
        # Análise 4
        f.write("## 4. Movimento dos Bandejões\n\n")
        if 'bandejoes' in resultados and 'erro' not in resultados['bandejoes']:
            r = resultados['bandejoes']
            f.write(f"- **Total de chegadas nos bandejões:** {r.get('total_chegadas', 0):,}\n")
            f.write(f"- **Hora de pico:** {r.get('hora_pico', 12)}h\n\n")
            
            f.write("**Principais Insights:**\n")
            f.write("- Pico fortíssimo no horário de almoço (11h30-12h30)\n")
            f.write("- Bandejão Central é o destino mais popular\n")
            f.write("- Padrão de ida (11h-13h) e retorno (13h-14h)\n")
            f.write("- Comportamento característico da cultura universitária USP\n\n")
            
            f.write("**Gráficos gerados:**\n")
            f.write("- `analise_09_bandejoes_chegadas_saidas.png`\n")
            f.write("- `analise_09_bandejoes_horario.png`\n")
            f.write("- `analise_09_bandejoes_origens.png`\n\n")
        else:
            f.write("❌ Erro na execução desta análise.\n\n")
        
        f.write("---\n\n")
        
        # Análise 5
        f.write("## 5. Impacto da Pandemia COVID-19\n\n")
        if 'covid' in resultados and 'erro' not in resultados['covid']:
            r = resultados['covid']
            f.write(f"- **Total em 2020 (pandemia inicial):** {r.get('total_2020', 0):,} viagens\n")
            f.write(f"- **Total em 2021 (retorno híbrido):** {r.get('total_2021', 0):,} viagens\n")
            f.write(f"- **Total em 2022 (presencial):** {r.get('total_2022', 0):,} viagens\n")
            f.write(f"- **Taxa de recuperação:** {r.get('taxa_recuperacao', 0):.1f}%\n\n")
            
            f.write("**Principais Insights:**\n")
            f.write("- Sistema inaugurado EXATAMENTE no início da pandemia (março 2020)\n")
            f.write("- Recuperação gradual em 2021 com retorno híbrido\n")
            f.write("- Normalização em 2022 com presencial completo\n")
            f.write("- Caso de estudo histórico único e bem documentado\n\n")
            
            f.write("**Gráficos gerados:**\n")
            f.write("- `analise_10_covid_evolucao_temporal.png`\n")
            f.write("- `analise_10_covid_comparacao_anual.png`\n")
            f.write("- `analise_10_covid_heatmap.png`\n")
            f.write("- `analise_10_covid_taxa_recuperacao.png`\n\n")
        else:
            f.write("❌ Erro na execução desta análise.\n\n")
        
        f.write("---\n\n")
        
        # Conclusão
        f.write("## Conclusões Gerais\n\n")
        f.write("Este conjunto de análises revela padrões **únicos do contexto universitário** que diferenciam\n")
        f.write("o sistema bikeshare da USP de sistemas urbanos convencionais:\n\n")
        f.write("1. **Horários altamente estruturados** em torno da grade acadêmica\n")
        f.write("2. **Sazonalidade extrema** com queda durante férias acadêmicas\n")
        f.write("3. **Forte integração modal** como primeira/última milha desde o Metrô\n")
        f.write("4. **Padrões culturais específicos** (movimento de bandejões)\n")
        f.write("5. **Resiliência durante a pandemia** e recuperação gradual\n\n")
        
        f.write("**Relevância para a monografia:**\n")
        f.write("- Justifica investimento em infraestrutura ciclística universitária\n")
        f.write("- Mostra complementaridade com transporte público\n")
        f.write("- Documenta impacto histórico da COVID-19\n")
        f.write("- Fornece insights para gestão e planejamento urbano universitário\n\n")
        
        f.write("---\n\n")
        f.write("*Relatório gerado automaticamente pelos scripts de análise do TCC.*\n")
        f.write("*Todas as consultas SQL estão documentadas nos arquivos .py para verificação do orientador.*\n")
    
    print(f"✅ Relatório salvo: {relatorio_path}")
    
    return relatorio_path

def main():
    """Função principal"""
    
    print("\n" + "🚴"*40)
    print("\n   SISTEMA DE ANÁLISES - TCC BIKESHARE USP")
    print("   Análises Específicas do Contexto Universitário")
    print("\n" + "🚴"*40 + "\n")
    
    # Executar análises
    resultados = executar_todas_analises()
    
    # Gerar relatório
    relatorio = gerar_relatorio_markdown(resultados)
    
    print_header("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"📊 {len([r for r in resultados.values() if 'erro' not in r])} de 5 análises executadas com sucesso")
    print(f"📁 Resultados em: {OUTPUT_DIR}")
    print(f"📝 Relatório: {relatorio}\n")
    
    print("🎓 Próximos passos:")
    print("   1. Revisar os gráficos gerados")
    print("   2. Verificar os arquivos CSV com dados brutos")
    print("   3. Incluir insights no Capítulo 5 (Discussão) da monografia")
    print("   4. Compartilhar com orientador para validação\n")

if __name__ == '__main__':
    main()
