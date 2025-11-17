#!/usr/bin/env python3
"""
Script 05: Relatório Consolidado para Monografia
=================================================

Este script gera um relatório consolidado com todas as estatísticas
e números para inclusão direta no texto da monografia.

Formato: LaTeX-friendly com comandos \newcommand para fácil inclusão.

Autor: Gabriel da Silva Alves
Data: Novembro 2025
Projeto: TCC - Análise de viagens de bicicletas compartilhadas na USP
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from ciclovias.models import Station, Trip
from django.db.models import Count, Avg, Max, Min, Q
from collections import defaultdict

# Criar diretório de saída
OUTPUT_DIR = 'analises_monografia/resultados'
os.makedirs(OUTPUT_DIR, exist_ok=True)

class RelatorioMonografia:
    """Classe para gerar relatório consolidado"""
    
    def __init__(self):
        self.stats = {}
        # 17 estacoes USP (PKs internos)
        usp_pks = [56826, 56659, 48848, 38637, 37915, 48852, 38476, 56642, 38582, 56762, 38425, 56965, 56713, 56654, 56640, 44878, 42323]
        self.estacoes_usp = Station.objects.filter(id__in=usp_pks)
        self.viagens_usp = Trip.objects.filter(
            Q(initial_station__in=self.estacoes_usp) | 
            Q(final_station__in=self.estacoes_usp)
        )
    
    def coletar_estatisticas_gerais(self):
        """Coleta estatísticas gerais do dataset"""
        print("\n📊 Coletando estatísticas gerais...")
        
        # Totais
        self.stats['total_viagens_bd'] = Trip.objects.count()
        self.stats['total_estacoes_bd'] = Station.objects.count()
        self.stats['total_estacoes_usp'] = self.estacoes_usp.count()
        self.stats['total_viagens_usp'] = self.viagens_usp.count()
        
        # Percentuais
        self.stats['percentual_viagens_usp'] = (
            self.stats['total_viagens_usp'] / self.stats['total_viagens_bd'] * 100
        )
        
        # Período temporal
        primeira = Trip.objects.order_by('start_time').first()
        ultima = Trip.objects.order_by('-start_time').first()
        
        if primeira and ultima:
            self.stats['data_primeira_viagem'] = primeira.start_time.strftime('%d/%m/%Y')
            self.stats['data_ultima_viagem'] = ultima.start_time.strftime('%d/%m/%Y')
            
            duracao = (ultima.start_time - primeira.start_time).days
            self.stats['dias_total_dataset'] = duracao
            self.stats['anos_total_dataset'] = duracao / 365.25
        
        # Viagens internas vs externas
        viagens_internas = Trip.objects.filter(
            initial_station__in=self.estacoes_usp,
            final_station__in=self.estacoes_usp
        ).count()
        
        self.stats['viagens_internas_usp'] = viagens_internas
        self.stats['viagens_externas_usp'] = self.stats['total_viagens_usp'] - viagens_internas
        self.stats['percentual_internas'] = (
            viagens_internas / self.stats['total_viagens_usp'] * 100
        )
    
    def coletar_top_estacoes(self):
        """Identifica as estações mais utilizadas"""
        print("\n📊 Identificando estações mais utilizadas...")
        
        dados_estacoes = []
        for estacao in self.estacoes_usp:
            saidas = Trip.objects.filter(initial_station=estacao).count()
            chegadas = Trip.objects.filter(final_station=estacao).count()
            total = saidas + chegadas
            
            dados_estacoes.append({
                'id': estacao.station_id,
                'nome': estacao.name,
                'total': total,
                'saidas': saidas,
                'chegadas': chegadas
            })
        
        # Ordenar por total
        dados_estacoes.sort(key=lambda x: x['total'], reverse=True)
        
        # Top 5
        for i in range(5):
            if i < len(dados_estacoes):
                e = dados_estacoes[i]
                self.stats[f'top{i+1}_estacao_id'] = e['id']
                self.stats[f'top{i+1}_estacao_nome'] = e['nome']
                self.stats[f'top{i+1}_estacao_viagens'] = e['total']
                self.stats[f'top{i+1}_estacao_saidas'] = e['saidas']
                self.stats[f'top{i+1}_estacao_chegadas'] = e['chegadas']
        
        # Bottom 3
        for i in range(3):
            if i < len(dados_estacoes):
                e = dados_estacoes[-(i+1)]
                self.stats[f'bottom{i+1}_estacao_id'] = e['id']
                self.stats[f'bottom{i+1}_estacao_nome'] = e['nome']
                self.stats[f'bottom{i+1}_estacao_viagens'] = e['total']
    
    def coletar_padroes_temporais(self):
        """Analisa padrões temporais"""
        print("\n📊 Analisando padrões temporais...")
        
        # Por hora
        horas_dict = defaultdict(int)
        for v in self.viagens_usp.values('start_hour'):
            if v['start_hour'] is not None:
                horas_dict[v['start_hour']] += 1
        
        if horas_dict:
            hora_pico = max(horas_dict.items(), key=lambda x: x[1])
            hora_vale = min(horas_dict.items(), key=lambda x: x[1])
            
            self.stats['hora_pico'] = hora_pico[0]
            self.stats['viagens_hora_pico'] = hora_pico[1]
            self.stats['hora_vale'] = hora_vale[0]
            self.stats['viagens_hora_vale'] = hora_vale[1]
        
        # Por dia da semana
        dias_dict = defaultdict(int)
        for v in self.viagens_usp.values('start_day'):
            if v['start_day'] is not None:
                dias_dict[v['start_day']] += 1
        
        dias_nomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        if dias_dict:
            dia_pico = max(dias_dict.items(), key=lambda x: x[1])
            self.stats['dia_semana_pico'] = dias_nomes[dia_pico[0]]
            self.stats['viagens_dia_pico'] = dia_pico[1]
            
            # Dias úteis vs fim de semana
            dias_uteis = sum(dias_dict[i] for i in range(5))
            fim_semana = sum(dias_dict[i] for i in range(5, 7))
            
            self.stats['viagens_dias_uteis'] = dias_uteis
            self.stats['viagens_fim_semana'] = fim_semana
            self.stats['media_dia_util'] = dias_uteis / 5
            self.stats['media_fim_semana'] = fim_semana / 2
            self.stats['percentual_dias_uteis'] = dias_uteis / (dias_uteis + fim_semana) * 100
        
        # Por mês
        meses_dict = defaultdict(int)
        for v in self.viagens_usp.values('month'):
            if v['month'] is not None:
                meses_dict[v['month']] += 1
        
        meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        if meses_dict:
            mes_pico = max(meses_dict.items(), key=lambda x: x[1])
            self.stats['mes_pico'] = meses_nomes[mes_pico[0]-1]
            self.stats['viagens_mes_pico'] = mes_pico[1]
            
            # Férias vs letivo
            meses_ferias = [1, 2, 7, 12]
            viagens_ferias = sum(meses_dict[m] for m in meses_ferias)
            viagens_letivo = sum(v for m, v in meses_dict.items() if m not in meses_ferias)
            
            self.stats['viagens_ferias'] = viagens_ferias
            self.stats['viagens_periodo_letivo'] = viagens_letivo
            self.stats['percentual_periodo_letivo'] = (
                viagens_letivo / (viagens_ferias + viagens_letivo) * 100
            )
    
    def coletar_fluxos(self):
        """Analisa fluxos entre estações"""
        print("\n📊 Analisando fluxos...")
        
        # Contar fluxos
        fluxos_dict = defaultdict(int)
        
        viagens = self.viagens_usp.select_related('initial_station', 'final_station')
        
        for viagem in viagens:
            if viagem.initial_station and viagem.final_station:
                if viagem.initial_station.station_id != viagem.final_station.station_id:
                    origem = viagem.initial_station
                    destino = viagem.final_station
                    chave = (origem.station_id, origem.name, destino.station_id, destino.name)
                    fluxos_dict[chave] += 1
        
        # Top 3 rotas
        fluxos_sorted = sorted(fluxos_dict.items(), key=lambda x: x[1], reverse=True)
        
        for i in range(3):
            if i < len(fluxos_sorted):
                (orig_id, orig_nome, dest_id, dest_nome), count = fluxos_sorted[i]
                self.stats[f'top{i+1}_rota_origem_id'] = orig_id
                self.stats[f'top{i+1}_rota_origem_nome'] = orig_nome
                self.stats[f'top{i+1}_rota_destino_id'] = dest_id
                self.stats[f'top{i+1}_rota_destino_nome'] = dest_nome
                self.stats[f'top{i+1}_rota_viagens'] = count
    
    def gerar_latex_commands(self):
        """Gera comandos LaTeX para as estatísticas"""
        print("\n📝 Gerando comandos LaTeX...")
        
        latex_file = f'{OUTPUT_DIR}/estatisticas_monografia.tex'
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write("% Estatísticas Geradas Automaticamente para a Monografia\n")
            f.write(f"% Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("% Uso: \\input{estatisticas_monografia.tex} no preâmbulo\n\n")
            
            f.write("% ====== ESTATÍSTICAS GERAIS ======\n")
            f.write(f"\\newcommand{{\\totalViagensDB}}{{{self.stats['total_viagens_bd']:,}}}\n")
            f.write(f"\\newcommand{{\\totalEstacoesDB}}{{{self.stats['total_estacoes_bd']}}}\n")
            f.write(f"\\newcommand{{\\totalEstacoesUSP}}{{{self.stats['total_estacoes_usp']}}}\n")
            f.write(f"\\newcommand{{\\totalViagensUSP}}{{{self.stats['total_viagens_usp']:,}}}\n")
            f.write(f"\\newcommand{{\\percentualViagensUSP}}{{{self.stats['percentual_viagens_usp']:.2f}}}\n")
            f.write(f"\\newcommand{{\\dataPrimeiraViagem}}{{{self.stats['data_primeira_viagem']}}}\n")
            f.write(f"\\newcommand{{\\dataUltimaViagem}}{{{self.stats['data_ultima_viagem']}}}\n")
            f.write(f"\\newcommand{{\\anosDataset}}{{{self.stats['anos_total_dataset']:.1f}}}\n\n")
            
            f.write("% ====== VIAGENS INTERNAS vs EXTERNAS ======\n")
            f.write(f"\\newcommand{{\\viagensInternasUSP}}{{{self.stats['viagens_internas_usp']:,}}}\n")
            f.write(f"\\newcommand{{\\viagensExternasUSP}}{{{self.stats['viagens_externas_usp']:,}}}\n")
            f.write(f"\\newcommand{{\\percentualInternas}}{{{self.stats['percentual_internas']:.1f}}}\n\n")
            
            f.write("% ====== TOP ESTAÇÕES ======\n")
            for i in range(1, 6):
                if f'top{i}_estacao_nome' in self.stats:
                    f.write(f"\\newcommand{{\\topEstacao{i}ID}}{{{self.stats[f'top{i}_estacao_id']}}}\n")
                    f.write(f"\\newcommand{{\\topEstacao{i}Nome}}{{{self.stats[f'top{i}_estacao_nome']}}}\n")
                    f.write(f"\\newcommand{{\\topEstacao{i}Viagens}}{{{self.stats[f'top{i}_estacao_viagens']:,}}}\n")
            
            f.write("\n% ====== PADRÕES TEMPORAIS ======\n")
            f.write(f"\\newcommand{{\\horaPico}}{{{self.stats.get('hora_pico', 0)}}}h\n")
            f.write(f"\\newcommand{{\\viagensHoraPico}}{{{self.stats.get('viagens_hora_pico', 0):,}}}\n")
            f.write(f"\\newcommand{{\\diaSemanaManage}}{{{self.stats.get('dia_semana_pico', 'N/A')}}}\n")
            f.write(f"\\newcommand{{\\percentualDiasUteis}}{{{self.stats.get('percentual_dias_uteis', 0):.1f}}}\n")
            f.write(f"\\newcommand{{\\mediaDiaUtil}}{{{self.stats.get('media_dia_util', 0):,.0f}}}\n")
            f.write(f"\\newcommand{{\\mediaFimSemana}}{{{self.stats.get('media_fim_semana', 0):,.0f}}}\n")
            f.write(f"\\newcommand{{\\mesPico}}{{{self.stats.get('mes_pico', 'N/A')}}}\n")
            f.write(f"\\newcommand{{\\percentualPeriodoLetivo}}{{{self.stats.get('percentual_periodo_letivo', 0):.1f}}}\n\n")
            
            f.write("% ====== TOP ROTAS ======\n")
            for i in range(1, 4):
                if f'top{i}_rota_viagens' in self.stats:
                    f.write(f"\\newcommand{{\\topRota{i}OrigemNome}}{{{self.stats[f'top{i}_rota_origem_nome']}}}\n")
                    f.write(f"\\newcommand{{\\topRota{i}DestinoNome}}{{{self.stats[f'top{i}_rota_destino_nome']}}}\n")
                    f.write(f"\\newcommand{{\\topRota{i}Viagens}}{{{self.stats[f'top{i}_rota_viagens']:,}}}\n")
        
        print(f"✅ Comandos LaTeX salvos em: {latex_file}")
    
    def gerar_relatorio_texto(self):
        """Gera relatório em formato texto"""
        print("\n📝 Gerando relatório em texto...")
        
        txt_file = f'{OUTPUT_DIR}/relatorio_completo.txt'
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(" " * 15 + "RELATÓRIO CONSOLIDADO - BIKESCIENCE USP\n")
            f.write(" " * 20 + "Análise de Viagens de Bicicletas Compartilhadas\n")
            f.write("="*80 + "\n\n")
            f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Autor: Gabriel da Silva Alves\n")
            f.write(f"Instituição: IME-USP\n")
            f.write("\n" + "="*80 + "\n")
            
            f.write("\n1. ESTATÍSTICAS GERAIS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total de viagens no banco de dados: {self.stats['total_viagens_bd']:,}\n")
            f.write(f"Total de estações cadastradas: {self.stats['total_estacoes_bd']}\n")
            f.write(f"Estações no campus USP: {self.stats['total_estacoes_usp']}\n")
            f.write(f"Viagens envolvendo USP: {self.stats['total_viagens_usp']:,} ({self.stats['percentual_viagens_usp']:.2f}%)\n")
            f.write(f"Período: {self.stats['data_primeira_viagem']} a {self.stats['data_ultima_viagem']}\n")
            f.write(f"Duração: {self.stats['anos_total_dataset']:.1f} anos\n")
            
            f.write("\n2. VIAGENS INTERNAS vs EXTERNAS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Viagens internas (USP → USP): {self.stats['viagens_internas_usp']:,} ({self.stats['percentual_internas']:.1f}%)\n")
            f.write(f"Viagens externas (USP ↔ Fora): {self.stats['viagens_externas_usp']:,} ({100-self.stats['percentual_internas']:.1f}%)\n")
            
            f.write("\n3. TOP 5 ESTAÇÕES MAIS UTILIZADAS\n")
            f.write("-" * 80 + "\n")
            for i in range(1, 6):
                if f'top{i}_estacao_nome' in self.stats:
                    f.write(f"{i}. {self.stats[f'top{i}_estacao_id']:3d} - {self.stats[f'top{i}_estacao_nome']:40s}: "
                           f"{self.stats[f'top{i}_estacao_viagens']:7,} viagens\n")
            
            f.write("\n4. PADRÕES TEMPORAIS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Hora de pico: {self.stats.get('hora_pico', 'N/A')}h ({self.stats.get('viagens_hora_pico', 0):,} viagens)\n")
            f.write(f"Dia da semana com mais viagens: {self.stats.get('dia_semana_pico', 'N/A')}\n")
            f.write(f"Viagens em dias úteis: {self.stats.get('percentual_dias_uteis', 0):.1f}%\n")
            f.write(f"Média por dia útil: {self.stats.get('media_dia_util', 0):,.0f} viagens\n")
            f.write(f"Média por dia de fim de semana: {self.stats.get('media_fim_semana', 0):,.0f} viagens\n")
            f.write(f"Mês com mais viagens: {self.stats.get('mes_pico', 'N/A')}\n")
            f.write(f"Viagens em período letivo: {self.stats.get('percentual_periodo_letivo', 0):.1f}%\n")
            
            f.write("\n5. TOP 3 ROTAS MAIS FREQUENTES\n")
            f.write("-" * 80 + "\n")
            for i in range(1, 4):
                if f'top{i}_rota_viagens' in self.stats:
                    f.write(f"{i}. {self.stats[f'top{i}_rota_origem_nome']} → "
                           f"{self.stats[f'top{i}_rota_destino_nome']}: "
                           f"{self.stats[f'top{i}_rota_viagens']:,} viagens\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("Fim do relatório\n")
            f.write("="*80 + "\n")
        
        print(f"✅ Relatório texto salvo em: {txt_file}")
    
    def executar(self):
        """Executa todas as coletas e gera relatórios"""
        print("\n" + "🚴" * 40)
        print(" " * 15 + "GERAÇÃO DE RELATÓRIO CONSOLIDADO")
        print(" " * 20 + "BikeScience USP")
        print("🚴" * 40)
        
        self.coletar_estatisticas_gerais()
        self.coletar_top_estacoes()
        self.coletar_padroes_temporais()
        self.coletar_fluxos()
        self.gerar_latex_commands()
        self.gerar_relatorio_texto()
        
        print("\n" + "="*80)
        print("  ✅ RELATÓRIO CONSOLIDADO GERADO COM SUCESSO!")
        print(f"  📁 Arquivos salvos em: {OUTPUT_DIR}/")
        print("="*80 + "\n")

def main():
    """Função principal"""
    try:
        relatorio = RelatorioMonografia()
        relatorio.executar()
        return 0
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
