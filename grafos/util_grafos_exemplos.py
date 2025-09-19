"""
Exemplos de uso da biblioteca util_grafos.py
"""

from util_grafos import GrafosBase, GrafosDijkstra

def get_g_exemplo():
    """Cria grafo de exemplo do professor"""
    grafo = GrafosDijkstra("Exemplo 1")
    
    # Cria dados no formato dicionário
    dados = {
        'A': {'B': 2, 'C': 1},
        'B': {'A': 2, 'D': 1},
        'C': {'A': 1, 'D': 3, 'E': 4},
        'D': {'B': 1, 'C': 3, 'F': 2},
        'E': {'C': 4, 'F': 2},
        'F': {'D': 2, 'E': 2}
    }
    
    grafo.carregar(dados)
    return grafo

def get_g_tarefa():
    """Cria grafo da tarefa"""
    grafo = GrafosDijkstra("Grafo da Tarefa")
    
    # Mapeamento: A:0 B:1 C:2 D:3 E:4 F:5
    dados = {
        'A': {'B': 4, 'C': 2},      # A:0 -> B:1, A:0 -> C:2
        'B': {'A': 4, 'D': 5, 'C': 1},  # B:1 -> A:0, B:1 -> D:3, B:1 -> C:2
        'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},  # C:2 connections
        'D': {'B': 5, 'C': 8, 'F': 6, 'E': 2},   # D:3 connections
        'E': {'C': 10, 'D': 2, 'F': 2},           # E:4 connections
        'F': {'D': 6, 'E': 2}                     # F:5 connections
    }
    
    grafo.carregar(dados)
    return grafo

def get_g_youtube():
    """Cria grafo do exemplo YouTube"""
    grafo = GrafosDijkstra("Exemplo YouTube")
    
    dados = {
        'A': {'B': 2, 'F': 3, 'D': 5},
        'B': {'A': 2, 'F': 4, 'E': 1, 'C': 7},
        'C': {'B': 7, 'E': 3, 'G': 4},
        'D': {'A': 5, 'E': 1, 'G': 1},
        'E': {'B': 1, 'D': 1, 'G': 3, 'C': 3},
        'F': {'A': 3, 'B': 4},
        'G': {'D': 1, 'E': 3, 'C': 4}
    }
    
    grafo.carregar(dados)
    return grafo

if __name__ == "__main__":
    # Exemplo de uso dos grafos
    print("=== Testando Grafos de Exemplo ===\n")
    
    # Testa grafo exemplo
    g1 = get_g_exemplo()
    print(f"Grafo Exemplo: {g1.nome_grafo}")
    print(f"Número de nós: {len(g1)}")
    caminho, custo = g1.obter_caminho_e_custo('A', 'F')
    print(f"Menor caminho A->F:", g1.movimentos.caminho_descrito())
    print(f'Custo esperado = 5 e custo obtido = {custo} >>>', '__o/' if custo == 5 else ':(')
    print()
    
    # Testa grafo tarefa
    g2 = get_g_tarefa()
    print(f"Grafo Tarefa: {g2.nome_grafo}")
    print(f"Número de nós: {len(g2)}")
    caminho, custo = g2.obter_caminho_e_custo('A', 'F')
    print(f"Menor caminho A->F:", g2.movimentos.caminho_descrito())
    print(f'Custo esperado = 12 e custo obtido = {custo} >>>', '__o/' if custo == 12 else ':(')
    print()
    
    # Testa grafo YouTube
    g3 = get_g_youtube()
    print(f"Grafo YouTube: {g3.nome_grafo}")
    print(f"Número de nós: {len(g3)}")
    caminho, custo = g3.obter_caminho_e_custo('A', 'C')
    print(f"Menor caminho A->C:", g3.movimentos.caminho_descrito())
    print(f'Custo esperado = 6 e custo obtido = {custo} >>>', '__o/' if custo == 6 else ':(')