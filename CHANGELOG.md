# Changelog - BikeScience Backend

## Versão 2.0 (Novembro 2025)

### Dataset Completo Implementado

- **Consolidação de dados expandida**: Processamento de todos os arquivos disponíveis (2018-2023)
- **Novo script principal**: `consolidate_tembici_COMPLETO.py` processa XLSXs e CSVs de todos os períodos
- **Dataset ampliado**: De 4.7M para 9.2M viagens (aumento de 95%)
- **Cobertura temporal**: 4.3 anos de dados (Janeiro/2018 - Abril/2022)

### Análises da Monografia

- **Pipeline de análises completo** em `analises_monografia/`
- **5 scripts de análise** cobrindo aspectos temporais, espaciais e de fluxo
- **Geração automática de gráficos** (PNG, 300 DPI) para inclusão na monografia
- **Estatísticas em LaTeX** para integração direta no texto
- **Script de execução em batch** (`executar_todas_analises.sh`)

### Melhorias no Processamento

- **Normalização de formatos**: Conversão automática de XLSX antigos para CSV padrão
- **Geocodificação**: Adição de coordenadas geográficas das estações
- **Validação de dados**: Verificação de integridade durante importação
- **Otimizações de performance**: Processamento em chunks para eficiência de memória

### Documentação

- **README principal reorganizado**: Estrutura mais clara e acadêmica
- **Documentação movida para** `/docs/`
- **Guias de processamento detalhados**

## Versão 1.0 (Inicial)

### Funcionalidades Iniciais

- **API REST Django** para consulta de viagens e estações
- **Endpoints GeoJSON** para ciclovias e hotzones
- **Processamento básico de CSVs**
- **Models Django**: Station e Trip
- **Interface Admin Django**

### Dados Iniciais

- Dataset parcial: 4.7M viagens (2020-2022)
- 492 estações cadastradas
- Infraestrutura cicloviária de São Paulo

---

**Desenvolvido por:** Gabriel da Silva Alves  
**Orientador:** Prof. Dr. Fabio Kon  
**Instituição:** IME-USP
