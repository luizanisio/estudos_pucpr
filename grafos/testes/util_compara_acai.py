import sys
sys.path.extend(['../','./'])

from util_grafos import GrafosDijkstra
from util_grafos_aestrela import GrafoAEstrela
from util_grafos_outros import GrafoBFS, GrafoDFS, GrafoGananciosa

arquivo_grafo = 'base_grafos/grafo_acai.json'

# Criando A* com heurística zero (equivalente ao Dijkstra)
astar = GrafoAEstrela()
dj = GrafosDijkstra()
gn = GrafoGananciosa()
for alg in [astar, dj, gn]:
    alg.carregar_json(arquivo_grafo)
    alg.encontrar_caminho('A', 'J')

print('Caminho Dijkstra:', dj.movimentos.get_caminho_completo())
print('Custo Dijkstra:', dj.movimentos.get_custo_total())
print('Caminho A*:', astar.movimentos.get_caminho_completo())
print('Custo A*:', astar.movimentos.get_custo_total())
print('Caminho Gananciosa:', gn.movimentos.get_caminho_completo())
print('Custo Gananciosa:', gn.movimentos.get_custo_total())
print()
