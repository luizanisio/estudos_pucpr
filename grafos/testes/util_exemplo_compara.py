import sys
sys.path.extend(['../','./'])

from util_grafos import GrafosDijkstra
from util_grafos_aestrela import GrafoAEstrela

dados = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8},
    'D': {'B': 5, 'C': 8}
}

# Criando A* com heurística zero (equivalente ao Dijkstra)
astar = GrafoAEstrela("A* Sem Heurística")
astar.carregar(dados)

# Definindo heurísticas zero para todos os pares (A* equivalente ao Dijkstra)
for origem in dados:
    for destino in dados:
        if origem != destino:
            astar.heuristicas[(origem, destino)] = 0

dj = GrafosDijkstra()
dj.carregar(dados)
dj.encontrar_caminho('A', 'D')
astar.encontrar_caminho('A', 'D')

print('Caminho Dijkstra A→C→B→D (2+1+5=8):', dj.movimentos.get_caminho_completo())
print('Custo Dijkstra:', dj.movimentos.get_custo_total())
print('Caminho A* A→C→B→D (2+1+5=8):', astar.movimentos.get_caminho_completo())
print('Custo A*:', astar.movimentos.get_custo_total())

