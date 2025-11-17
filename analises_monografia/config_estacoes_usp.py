#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO DAS ESTAÇÕES USP
=============================

Define as 17 estações consideradas como parte do Campus USP Butantã.
IMPORTANTE: Usar estes PKs internos em TODAS as análises.

Estações EXCLUÍDAS (fora do campus):
- 244 - Metrô Butantã (estação de metrô externa)
- 255 - Estação Tiradentes (fora do perímetro)
"""

# PKs internos (IDs do banco) das 17 estações USP
ESTACOES_USP_PKS = [
    56826,  # 242 - Letras
    56659,  # 243 - Bancos/Reitoria
    48848,  # 245 - P1
    38637,  # 246 - Portão CPTM
    37915,  # 247 - CEPE
    48852,  # 248 - Biblioteca Brasiliana
    38476,  # 249 - Bandejão Central
    56642,  # 250 - Bandejão Química
    38582,  # 251 - FAU
    56762,  # 252 - Psicologia
    38425,  # 253 - Pedalusp Biênio
    56965,  # 254 - Terminal de Ônibus USP
    56713,  # 256 - Bandejão Prefeitura
    56654,  # 257 - Hospital Universitário
    56640,  # 258 - Odontologia
    44878,  # 259 - Vila Indiana
    42323,  # 260 - P3
]

# IDs externos (station_id) correspondentes
ESTACOES_USP_STATION_IDS = [242, 243, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 256, 257, 258, 259, 260]

# Total esperado de viagens (para validação)
TOTAL_VIAGENS_USP_ESPERADO = 59921
TOTAL_VIAGENS_INTERNAS_ESPERADO = 34126

# Mapeamento de categorias
ESTACOES_BANDEJAO_PKS = {
    38476: 'Bandejão Central',        # 249
    56642: 'Bandejão Química',        # 250
    56713: 'Bandejão Prefeitura'      # 256
}

ESTACOES_PORTAL_PKS = {
    38637: 'PORTÃO CPTM',      # 246
    48848: 'P1',               # 245
    44878: 'Vila Indiana',     # 259
}
