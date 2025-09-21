# Algoritmos de Busca em Grafos - Trabalho 02

## Descrição Geral
O trabalho tem como objetivo implementar e comparar diferentes algoritmos de busca em grafos:
i) Dijkstra (vídeo https://www.youtube.com/watch?v=CmIQ29cUGiE ), 
ii) Busca Ambicioso/Gananciosa, 
iii) A*, 
iv) Busca em Profundidade (DFS) e 
v) Busca em Largura (BFS). 

A análise será realizada em um grafo representando um problema real (como rotas logísticas, redes de transporte, etc), avaliando a eficiência, corretude e custo computacional de cada abordagem.


## Objetivos de Aprendizagem
● Implementar os algoritmos de Dijkstra, Busca Gananciosa, A*, DFS e BFS em Python
● Construir um grafo com 10 a 15 nós, com arestas de diferentes pesos, representando um problema real
● **Analisar performance detalhada** com métricas de tempo, memória e eficiência
● Visualizar o grafo utilizando a biblioteca Pyvis
● Comparar o desempenho dos algoritmos com **métricas quantitativas precisas**
● Desenvolver análise crítica fundamentada em dados de performance

## Requisitos

### Grafo
● Criar um grafo com 10 a 15 vértices, com múltiplas arestas ponderadas
● Representar um problema realista (ex.: rotas de entrega, redes de transporte)
● **Usar labels descritivos** para melhor interpretação semântica
● Utilizar a biblioteca Pyvis para visualização do grafo

### Algoritmos
● **Dijkstra**: calcular o caminho mínimo considerando custos acumulados
● **Busca Gananciosa**: aplicar heurística simples (ex.: distância estimada ao destino)
● **A***: combinar custo acumulado com heurística para garantir soluções ótimas
● **DFS e BFS**: aplicar em busca de caminhos, comparando desempenho
● **Análise de Performance**: medir tempo, memória e eficiência para cada algoritmo

## Casos de Teste
● Executar pelo menos cinco pares distintos de nós como origem e destino
● **Coletar métricas de performance** para cada execução
● Comparar resultados com base em dados quantitativos

# Resumo simplificado da Implementação

## Estrutura do Projeto

O projeto está organizado em módulos especializados:

- **`util_grafos.py`**: Classe base `GrafosBase` e implementação do algoritmo Dijkstra
- **`util_grafos_aestrela.py`**: Implementação do algoritmo A* com suporte a heurísticas
- **`util_grafos_outros.py`**: Implementação dos algoritmos BFS, DFS e Busca Gananciosa  
- **`util_visualizacao.py`**: Classe `VisualizacaoGrafo` para gerar visualizações HTML interativas
- **`util_graficos.py`**: Funções para gerar gráficos comparativos dos resultados
- **`rodar_experimento.py`**: Script principal para executar todos os algoritmos e coletar métricas

## Grafo de Teste

O projeto utiliza um grafo realista representando uma **rede de distribuição logística** com 13 nós:
- Nós com labels descritivos (Centro de Distribuição, Shopping Center, Hospital Municipal, etc.)
- Arestas ponderadas representando distâncias em quilômetros
- Estrutura conectada permitindo múltiplos caminhos entre origem e destino

## Algoritmos Implementados

1. **Dijkstra**: Algoritmo ótimo para menor caminho com pesos positivos
2. **A***: Algoritmo ótimo usando heurística (distância euclidiana) para otimizar busca
3. **Busca Gananciosa**: Algoritmo não-ótimo usando apenas heurística
4. **BFS (Busca em Largura)**: Explora nível por nível, ótimo para grafos não-ponderados
5. **DFS (Busca em Profundidade)**: Explora um caminho até o fim antes de retroceder

## Métricas Coletadas

Para cada execução dos algoritmos, o sistema coleta:
- **Tempo de execução** (com média e desvio padrão de 5 execuções)
- **Custo total** do caminho encontrado
- **Número de nós no caminho** final
- **Número de nós visitados** durante a busca
- **Número de iterações** realizadas
- **Número de nós expandidos**

## Visualizações Geradas

- **Grafos HTML interativos**: Visualização colorida dos caminhos com pyvis
- **Gráficos comparativos**: Análise visual das métricas de performance
- **Dados CSV**: Exportação dos resultados para análise posterior

## Como Executar

```bash
python rodar_experimento.py
```

O script executa automaticamente todos os algoritmos no grafo de teste (rotas de estudo: Ex. A→J) e gera:
- Arquivo CSV com métricas detalhadas em `/resultados/`
- Visualizações HTML interativas para cada algoritmo
- Gráfico comparativo de performance