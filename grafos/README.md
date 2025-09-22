# Algoritmos de Busca em Grafos

Este projeto implementa e compara diferentes algoritmos de busca em grafos, incluindo algoritmos de busca de menor caminho e algoritmos de busca geral.

## Estrutura do Projeto

```
trab02/
├── util_grafos.py              # Implementação do algoritmo de Dijkstra
├── util_grafos_aestrela.py     # Implementação do algoritmo A*
├── util_grafos_outros.py       # Implementação de BFS, DFS e Busca Gananciosa
├── testes/
│   └── comparacao.py           # Script de comparação entre algoritmos
├── README.md                   # Documentação principal
└── README_VisualizacaoGrafo.md # Documentação de visualização
```

## Algoritmos Implementados

### Algoritmos de Menor Caminho

#### Dijkstra
- **Classe**: `GrafosDijkstra`
- **Características**: Encontra o menor caminho entre dois vértices
- **Complexidade**: O(V² + E) onde V é o número de vértices e E o número de arestas
- **Garantia**: Sempre encontra o caminho ótimo para grafos com pesos não-negativos

#### A* (A-estrela)
- **Classe**: `GrafoAEstrela`
- **Características**: Algoritmo heurístico que pode ser mais eficiente que Dijkstra
- **Funcionalidade**: Utiliza função heurística para guiar a busca
- **Flexibilidade**: Pode ser configurado como Dijkstra (heurística = 0)

### Algoritmos de Busca Geral

#### Busca em Largura (BFS)
- **Características**: Explora vértices nivel por nivel
- **Complexidade**: O(V + E)
- **Garantia**: Encontra o caminho com menor número de arestas
- **Estrutura**: Utiliza fila (FIFO) para controle da busca

#### Busca em Profundidade (DFS)
- **Características**: Explora um caminho até o final antes de retroceder
- **Complexidade**: O(V + E)
- **Comportamento**: Pode não encontrar o caminho ótimo
- **Estrutura**: Utiliza pilha (LIFO) ou recursão

#### Busca Gananciosa
- **Características**: Seleciona sempre o próximo vértice com menor heurística
- **Comportamento**: Mais rápida que A* mas não garante otimalidade
- **Funcionalidade**: Utiliza apenas a função heurística para decisões
- **Aplicação**: Útil quando velocidade é mais importante que otimalidade

## Uso Básico

### Dijkstra
```python
from util_grafos import GrafosDijkstra

# Criar instância
dijkstra = GrafosDijkstra()

# Carregar grafo (dicionário de adjacências com pesos)
dados_grafo = {
    'vertice1': {'vertice2': peso, 'vertice3': peso},
    'vertice2': {'vertice1': peso, 'vertice4': peso},
    # ...
}
dijkstra.carregar(dados_grafo)

# Encontrar caminho
dijkstra.encontrar_caminho('origem', 'destino')

# Obter resultados
caminho = dijkstra.movimentos.get_caminho_completo()
custo = dijkstra.movimentos.get_custo_total()
```

### A*
```python
from util_grafos_aestrela import GrafoAEstrela

# Criar instância
astar = GrafoAEstrela("Nome do Algoritmo")

# Carregar grafo
astar.carregar(dados_grafo)

# Definir heurísticas (opcional - padrão é 0)
astar.heuristicas[(origem, destino)] = valor_heuristico

# Encontrar caminho
astar.encontrar_caminho('origem', 'destino')

# Obter resultados
caminho = astar.movimentos.get_caminho_completo()
custo = astar.movimentos.get_custo_total()
```

### Algoritmos de Busca Geral
```python
from util_grafos_outros import BFS, DFS, BuscaGananciosa

# BFS - Busca em Largura
bfs = BFS()
bfs.carregar(dados_grafo)
bfs.encontrar_caminho('origem', 'destino')

# DFS - Busca em Profundidade  
dfs = DFS()
dfs.carregar(dados_grafo)
dfs.encontrar_caminho('origem', 'destino')

# Busca Gananciosa
gananciosa = BuscaGananciosa()
gananciosa.carregar(dados_grafo)
# Definir heurísticas (obrigatório para busca gananciosa)
gananciosa.heuristicas[(origem, destino)] = valor_heuristico
gananciosa.encontrar_caminho('origem', 'destino')

# Obter resultados (mesmo padrão para todos)
caminho = algoritmo.movimentos.get_caminho_completo()
custo = algoritmo.movimentos.get_custo_total()
```

## Formato dos Dados

Os grafos devem ser representados como dicionários de adjacências:
```python
grafo = {
    'vertice_origem': {
        'vertice_destino': peso_aresta,
        'outro_vertice': peso_aresta
    },
    'outro_vertice_origem': {
        # adjacências...
    }
}
```

## Comparação de Algoritmos

O arquivo `testes/comparacao.py` demonstra como comparar os algoritmos:
- Carrega o mesmo grafo em diferentes implementações
- Executa a busca da mesma origem para o mesmo destino
- Compara caminhos encontrados e custos totais
- Analisa diferenças de performance e qualidade das soluções

### Características Comparativas

| Algoritmo | Otimalidade | Complexidade | Heurística | Estrutura de Dados |
|-----------|-------------|--------------|------------|-------------------|
| Dijkstra | Sempre | O(V² + E) | Não | Fila de prioridade |
| A* | Com h admissível | O(b^d) | Sim | Fila de prioridade |
| BFS | Para grafos não-ponderados | O(V + E) | Não | Fila (FIFO) |
| DFS | Não | O(V + E) | Não | Pilha (LIFO) |
| Busca Gananciosa | Não | O(V + E) | Sim | Baseada em heurística |

## Características dos Resultados

Todos os algoritmos fornecem:
- **Caminho completo**: Sequência de vértices da origem ao destino
- **Custo total**: Soma dos pesos das arestas no caminho encontrado
- **Movimentos**: Objeto que armazena o histórico da execução

## Observações

### Sobre Otimalidade
- **Dijkstra**: Sempre encontra o caminho ótimo
- **A***: Encontra o caminho ótimo se a heurística for admissível
- **BFS**: Encontra o caminho com menor número de arestas
- **DFS**: Não garante otimalidade
- **Busca Gananciosa**: Não garante otimalidade, mas pode ser mais rápida

### Sobre Heurísticas
- A* com heurística zero é funcionalmente equivalente ao Dijkstra
- Busca Gananciosa depende completamente da qualidade da heurística
- Heurísticas inadmissíveis podem comprometer a otimalidade do A*

### Considerações de Uso
- Para grafos pequenos: qualquer algoritmo pode ser adequado
- Para garantia de otimalidade: use Dijkstra ou A* com heurística admissível
- Para rapidez sem garantia de otimalidade: use Busca Gananciosa ou DFS
- Para exploração sistemática: use BFS ou DFS
- Os algoritmos assumem grafos com pesos não-negativos (exceto BFS e DFS)