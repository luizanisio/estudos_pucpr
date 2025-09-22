# 🎨 Visualização de Grafos - Guia de Uso

## 📋 Resumo

A classe `VisualizacaoGrafo` gera visualizações interativas de algoritmos de busca em grafos usando a biblioteca `pyvis`. 

**Status: ✅ Implementada e funcional**

## 🔧 Principais Funcionalidades

### Cores dos Nós:
- 🔵 **Azul**: Nó de origem
- 🔴 **Vermelho**: Nó de destino  
- 🟢 **Verde**: Nós do caminho encontrado
- 🟡 **Amarelo**: Nós visitados durante a busca
- ⚪ **Cinza**: Nós não visitados

### Arestas:
- 🟢 **Verde espesso**: Arestas do caminho final
- ⚪ **Cinza tracejado**: Outras arestas

### Informações Exibidas:
- Labels descritivos nos nós
- Pesos das arestas
- Estatísticas do algoritmo no título
- Interatividade (zoom, arraste, tooltips)

## 📖 Como Usar

### Uso Básico:
```python
from util_visualizacao import VisualizacaoGrafo
from util_grafos_outros import GrafoBFS

# 1. Criar e executar algoritmo
grafo = GrafoBFS("Meu Grafo")
grafo.carregar_json('base_grafos/grafo_acai.json')
grafo.encontrar_caminho('A', 'J')

# 2. Gerar visualização
viz = VisualizacaoGrafo(grafo, "Busca em Largura")
arquivo = viz.gerar_grafo_visual("resultado", 'A', 'J')

# 3. Abrir no navegador: resultado.html
```

### Uso Básico:
```python
from util_visualizacao import VisualizacaoGrafo
from util_grafos_outros import GrafoBFS

# 1. Criar e executar algoritmo
grafo = GrafoBFS()
grafo.carregar_json('base_grafos/grafo_acai.json')
grafo.encontrar_caminho('A', 'J')

# 2. Gerar visualização
viz = VisualizacaoGrafo(grafo, "Busca em Largura")
arquivo = viz.gerar_grafo_visual("resultado", 'A', 'J')

# 3. Abrir arquivo resultado.html no navegador
```

### Exemplo Completo:
```python
# Executar script principal que gera todas as visualizações
python rodar_experimento.py

# Visualizações são salvas em ./resultados/
# Exemplo: grafo_acai_BFS_A_J.html
```

## 📦 Dependências

### Obrigatória:
- **pyvis** - Instalação automática se não encontrada

### Opcional:
- **selenium** + **ChromeDriver** - Para gerar imagens PNG

```bash
pip install pyvis
# Para PNG (opcional):
pip install selenium
```

## 📁 Arquivos Gerados

Ao executar `rodar_experimento.py`, são criados na pasta `resultados/`:

- **HTML interativos**: `grafo_acai_[ALGORITMO]_A_J.html`
- **Dados CSV**: `grafo_acai_A_J.csv` (métricas de performance)  
- **Gráficos**: `Comparando algoritmos_A_J_graficos.png`

## � Métodos Principais

### `VisualizacaoGrafo(grafo, titulo)`
Cria objeto de visualização a partir de um grafo já executado.

### `gerar_grafo_visual(nome_arquivo, origem, destino)`
Gera arquivo HTML interativo com a visualização colorida.

**Retorna**: Caminho do arquivo HTML gerado

## ✅ Testado e Funcional

A classe está completamente implementada e testada com todos os algoritmos:
- ✅ BFS, DFS, Dijkstra, A*, Busca Gananciosa
- ✅ Cores diferenciadas para nós e arestas
- ✅ Geração automática de arquivos HTML
- ✅ Compatível com diferentes grafos JSON

**Pronto para uso em experimentos de algoritmos de busca!**

# Visualização de Grafos

Este documento descreve as funcionalidades de visualização disponíveis para os algoritmos de busca em grafos implementados no projeto.

## Visão Geral

O sistema de visualização permite acompanhar a execução dos algoritmos Dijkstra e A* de forma gráfica, facilitando a compreensão do processo de busca e comparação entre diferentes abordagens.

## Funcionalidades de Visualização

### Representação do Grafo
- **Vértices**: Representados como círculos ou nós
- **Arestas**: Linhas conectando os vértices com pesos exibidos
- **Direcionamento**: Suporte para grafos direcionados e não-direcionados

### Acompanhamento da Execução
- **Estados dos Vértices**: Diferentes cores para vértices visitados, não visitados e em processamento
- **Caminho Atual**: Destacamento visual do caminho sendo explorado
- **Fila de Prioridade**: Visualização dos vértices na fila de processamento

### Comparação de Algoritmos
- **Execução Paralela**: Visualização lado a lado de Dijkstra e A*
- **Métricas em Tempo Real**: Custo atual, número de vértices visitados
- **Caminho Final**: Destacamento do caminho ótimo encontrado

## Classes de Movimento

### Funcionalidades Básicas
```python
# Obter caminho completo como lista de vértices
caminho = movimentos.get_caminho_completo()

# Obter custo total do caminho
custo = movimentos.get_custo_total()
```

### Rastreamento de Estados
- **Histórico de Movimentos**: Registro de cada passo da execução
- **Estados Intermediários**: Captura de estados do algoritmo em cada iteração
- **Backtracking**: Capacidade de reconstruir o caminho ótimo

## Configuração da Visualização

### Parâmetros Visuais
- **Cores**: Personalizáveis para diferentes estados dos vértices
- **Tamanhos**: Ajustáveis para vértices e espessura das arestas
- **Layout**: Algoritmos automáticos de posicionamento dos vértices

### Controles de Animação
- **Velocidade**: Controle da velocidade de execução da animação
- **Pause/Play**: Controle manual da execução
- **Step-by-Step**: Execução passo a passo para análise detalhada

## Interpretação dos Resultados

### Cores Padrão dos Vértices
- **Branco/Cinza Claro**: Vértices não visitados
- **Amarelo/Laranja**: Vértices na fila de prioridade
- **Verde**: Vértices processados
- **Azul**: Vértice de origem
- **Vermelho**: Vértice de destino
- **Roxo**: Caminho final ótimo

### Métricas Exibidas
- **Custo Acumulado**: Custo do caminho até cada vértice
- **Heurística**: Valor da função heurística (apenas A*)
- **f(n) = g(n) + h(n)**: Função de avaliação total (apenas A*)

## Análise Comparativa

### Diferenças Visuais
- **Dijkstra**: Exploração mais uniforme do espaço de busca
- **A***: Busca direcionada pela heurística
- **Eficiência**: Comparação visual do número de vértices explorados

### Métricas de Performance
- **Número de Vértices Visitados**: Comparação da eficiência
- **Tempo de Execução**: Análise de performance temporal
- **Qualidade da Solução**: Verificação da otimalidade

## Uso Avançado

### Heurísticas Personalizadas
```python
# Definir heurística customizada para A*
def heuristica_personalizada(origem, destino):
    # Implementar lógica da heurística
    return valor_heuristico

# Aplicar ao grafo A*
for origem in vertices:
    for destino in vertices:
        if origem != destino:
            astar.heuristicas[(origem, destino)] = heuristica_personalizada(origem, destino)
```

### Exportação de Resultados
- **Imagens**: Salvamento do estado final da visualização
- **Dados**: Exportação das métricas de execução
- **Animações**: Geração de GIFs ou vídeos da execução

## Limitações

- A visualização é otimizada para grafos de tamanho pequeno a médio
- Grafos muito densos podem apresentar sobreposição visual
- A performance da animação depende da complexidade do grafo

## Extensibilidade

O sistema de visualização foi projetado para ser extensível:
- **Novos Algoritmos**: Fácil integração de outros algoritmos de busca
- **Diferentes Representações**: Suporte para diferentes tipos de grafo
- **Métricas Customizadas**: Adição de novas métricas de análise