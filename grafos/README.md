# Algoritmos de Busca em Grafos - Trabalho 02

## Descrição Geral
O trabalho tem como objetivo implementar e comparar diferentes algoritmos de busca em grafos:
i) Dijkstra, 
ii) Busca Ambicioso/Gananciosa, 
iii) A*, 
iv) Busca em Profundidade (DFS) e v)
Busca em Largura (BFS). A análise será realizada em um grafo representando um problema real (como rotas logísticas, redes de transporte, etc), avaliando a eficiência, corretude e custo computacional de cada abordagem.


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