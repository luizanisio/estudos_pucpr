from util_grafos import GrafosBase
from collections import deque


# https://medium.com/@anwarhermuche/m%C3%A9todos-de-busca-em-grafos-bfs-dfs-cf17761a0dd9

class GrafoBFS(GrafosBase):
    """ Implementa o algoritmo BFS (Busca em Largura) para encontrar caminho entre nós. """
    def __init__(self, nome_grafo="Grafo BFS"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'BFS'

    def encontrar_caminho(self, inicio, fim):
        """
        Implementa o algoritmo BFS para encontrar caminho entre dois nós.
        
        Parâmetros:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
            
        Retorna:
            bool: True se encontrou caminho, False caso contrário
        """
        # PASSO 1: Preparação inicial
        # Limpa registros de movimentos anteriores
        self.movimentos.reset()
        
        # Verifica se os pontos de início e fim existem no grafo
        if inicio not in self.nos or fim not in self.nos:
            return False
        
        # PASSO 2: Configuração das estruturas de dados do BFS
        # Fila para explorar nós (FIFO - primeiro a entrar, primeiro a sair)
        fila = deque([inicio])
        # Conjunto de nós já visitados
        visitados = set()
        # Dicionário para rastrear predecessores (para reconstruir o caminho)
        predecessores = {}
        
        # PASSO 3: Loop principal - explora nós nível por nível
        while fila:
            # PASSO 3.1: Remove o primeiro nó da fila
            no_atual = fila.popleft()
            
            # PASSO 3.2: Se já foi visitado, pula
            if no_atual in visitados:
                continue
                
            # PASSO 3.3: Marca como visitado
            visitados.add(no_atual)
            # Registra o nó como visitado no sistema de movimentos
            self.movimentos.marcar_visitado(no_atual)
            
            # PASSO 3.4: Verifica se chegou no destino
            if no_atual == fim:
                # Reconstrói e registra o caminho
                caminho_encontrado = self._reconstruir_caminho(predecessores, fim)
                for nodo in caminho_encontrado:
                    self.movimentos.mover_para(nodo)
                return True
            
            # PASSO 3.5: Explora todos os vizinhos
            for vizinho, _ in self._adjacentes_de(no_atual):
                # Se o vizinho não foi visitado e não está na fila
                if vizinho not in visitados and vizinho not in predecessores:
                    # Adiciona à fila para explorar depois
                    fila.append(vizinho)
                    # Registra de onde veio (para reconstruir o caminho)
                    predecessores[vizinho] = no_atual
        
        # PASSO 4: Se chegou aqui, não existe caminho
        return False

    def _reconstruir_caminho(self, predecessores, no_final):
        """Reconstrói o caminho a partir dos predecessores
        
        Args:
            predecessores: Dicionário de predecessores
            no_final: Nó final do caminho
            
        Returns:
            list: Lista de nós formando o caminho
        """
        caminho = []
        no_atual = no_final
        
        # Volta pelo caminho seguindo os predecessores
        while no_atual is not None:
            caminho.append(no_atual)
            no_atual = predecessores.get(no_atual)
        
        # Inverte para ficar na ordem correta (início -> fim)
        caminho.reverse()
        return caminho


class GrafoDFS(GrafosBase):
    """ Implementa o algoritmo DFS (Busca em Profundidade) para encontrar caminho entre nós. """
    def __init__(self, nome_grafo="Grafo DFS"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'DFS'

    def encontrar_caminho(self, inicio, fim):
        """
        Implementa o algoritmo DFS para encontrar caminho entre dois nós.
        
        Parâmetros:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
            
        Retorna:
            bool: True se encontrou caminho, False caso contrário
        """
        # PASSO 1: Preparação inicial
        # Limpa registros de movimentos anteriores
        self.movimentos.reset()
        
        # Verifica se os pontos de início e fim existem no grafo
        if inicio not in self.nos or fim not in self.nos:
            return False
        
        # PASSO 2: Configuração das estruturas de dados do DFS
        # Pilha para explorar nós (LIFO - último a entrar, primeiro a sair)
        pilha = [inicio]
        # Conjunto de nós já visitados
        visitados = set()
        # Dicionário para rastrear predecessores (para reconstruir o caminho)
        predecessores = {}
        
        # PASSO 3: Loop principal - explora em profundidade
        while pilha:
            # PASSO 3.1: Remove o último nó da pilha
            no_atual = pilha.pop()
            
            # PASSO 3.2: Se já foi visitado, pula
            if no_atual in visitados:
                continue
                
            # PASSO 3.3: Marca como visitado
            visitados.add(no_atual)
            # Registra o nó como visitado no sistema de movimentos
            self.movimentos.marcar_visitado(no_atual)
            
            # PASSO 3.4: Verifica se chegou no destino
            if no_atual == fim:
                # Reconstrói e registra o caminho
                caminho_encontrado = self._reconstruir_caminho(predecessores, fim)
                for nodo in caminho_encontrado:
                    self.movimentos.mover_para(nodo)
                return True
            
            # PASSO 3.5: Explora todos os vizinhos (em ordem reversa para manter consistência)
            vizinhos = self._adjacentes_de(no_atual)
            for vizinho, _ in reversed(vizinhos):
                # Se o vizinho não foi visitado
                if vizinho not in visitados and vizinho not in predecessores:
                    # Adiciona à pilha para explorar em profundidade
                    pilha.append(vizinho)
                    # Registra de onde veio (para reconstruir o caminho)
                    predecessores[vizinho] = no_atual
        
        # PASSO 4: Se chegou aqui, não existe caminho
        return False

    def _reconstruir_caminho(self, predecessores, no_final):
        """Reconstrói o caminho a partir dos predecessores
        
        Args:
            predecessores: Dicionário de predecessores
            no_final: Nó final do caminho
            
        Returns:
            list: Lista de nós formando o caminho
        """
        caminho = []
        no_atual = no_final
        
        # Volta pelo caminho seguindo os predecessores
        while no_atual is not None:
            caminho.append(no_atual)
            no_atual = predecessores.get(no_atual)
        
        # Inverte para ficar na ordem correta (início -> fim)
        caminho.reverse()
        return caminho


class GrafoGananciosa(GrafosBase):
    """ Implementa o algoritmo Greedy Best-First Search (Busca Gananciosa). """
    def __init__(self, nome_grafo="Grafo Busca Gananciosa"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'Gananciosa'

    def _calcular_heuristica(self, no_origem, no_destino):
        # Usa o método heurística da classe base se disponível
        return self._heuristica(no_origem, no_destino)

    def encontrar_caminho(self, inicio, fim):
        """
        Implementa o algoritmo Greedy Best-First Search.
        
        Parâmetros:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
            
        Retorna:
            bool: True se encontrou caminho, False caso contrário
        """
        import heapq
        
        # PASSO 1: Preparação inicial
        # Limpa registros de movimentos anteriores
        self.movimentos.reset()
        
        # Verifica se os pontos de início e fim existem no grafo
        if inicio not in self.nos or fim not in self.nos:
            return False
        
        # PASSO 2: Configuração das estruturas GBFS (OPEN/CLOSED)
        # OPEN: fila de prioridade ordenada por heurística (h(n))
        heuristica_inicial = self._calcular_heuristica(inicio, fim)
        open_list = [(heuristica_inicial, 0, inicio)]  # (heurística, contador, nó)
        # CLOSED: conjunto de nós já expandidos
        closed_set = set()
        # Predecessores para reconstruir o caminho
        predecessores = {}
        # Contador para desempate (ordem de inserção)
        contador = 1
        
        # PASSO 3: Loop principal do GBFS
        while open_list:
            # PASSO 3.1: Remove o nó com menor heurística (mais promissor)
            _, _, no_atual = heapq.heappop(open_list)
            
            # PASSO 3.2: Se já foi expandido, pula (evita reprocessamento)
            if no_atual in closed_set:
                continue
            
            # PASSO 3.3: Marca como expandido e registra visita
            closed_set.add(no_atual)
            self.movimentos.marcar_visitado(no_atual)
            
            # PASSO 3.4: Verifica se chegou no destino
            if no_atual == fim:
                # Reconstrói e registra o caminho encontrado
                caminho_encontrado = self._reconstruir_caminho(predecessores, fim)
                for nodo in caminho_encontrado:
                    self.movimentos.mover_para(nodo)
                return True
            
            # PASSO 3.5: Expande todos os vizinhos (gera sucessores)
            for vizinho, _ in self._adjacentes_de(no_atual):
                # Se o vizinho não foi expandido ainda
                if vizinho not in closed_set:
                    # Calcula heurística para o vizinho
                    heuristica = self._calcular_heuristica(vizinho, fim)
                    # Adiciona à fila de prioridade
                    heapq.heappush(open_list, (heuristica, contador, vizinho))
                    contador += 1
                    # CORREÇÃO: Registra predecessor apenas se não existe ou se este é melhor
                    # Para GBFS puro, sempre atualiza o predecessor com a última expansão
                    predecessores[vizinho] = no_atual
        
        # PASSO 4: Se a OPEN ficou vazia, não existe caminho
        return False

    def _reconstruir_caminho(self, predecessores, no_final):
        """Reconstrói o caminho a partir dos predecessores
        
        Args:
            predecessores: Dicionário de predecessores
            no_final: Nó final do caminho
            
        Returns:
            list: Lista de nós formando o caminho
        """
        caminho = []
        no_atual = no_final
        
        # Volta pelo caminho seguindo os predecessores
        while no_atual is not None:
            caminho.append(no_atual)
            no_atual = predecessores.get(no_atual)
        
        # Inverte para ficar na ordem correta (início -> fim)
        caminho.reverse()
        return caminho


if __name__ == "__main__":
    # Teste das três implementações
    print("=== Testando algoritmos de busca ===\n")
    
    # Carrega o grafo de exemplo
    arquivo_grafo = "base_grafos/grafo_acai.json"
    origem, destino = 'A', 'J'
    
    # Teste BFS
    print("1. Testando BFS (Busca em Largura)")
    grafo_bfs = GrafoBFS()
    grafo_bfs.carregar_json(arquivo_grafo)
    
    if grafo_bfs.encontrar_caminho(origem, destino):
        caminho = grafo_bfs.movimentos.get_caminho_completo()
        custo_total = grafo_bfs.movimentos.get_custo_total()
        visitados = len(grafo_bfs.movimentos.visitados)
        print(f"   Caminho BFS: {' -> '.join(caminho)} (custo: {custo_total}, visitados: {visitados})")
    else:
        print(f"   BFS: Caminho não encontrado de {origem} para {destino}")
    
    # Teste DFS
    print("\n2. Testando DFS (Busca em Profundidade)")
    grafo_dfs = GrafoDFS()
    grafo_dfs.carregar_json(arquivo_grafo)
    
    if grafo_dfs.encontrar_caminho(origem, destino):
        caminho = grafo_dfs.movimentos.get_caminho_completo()
        custo_total = grafo_dfs.movimentos.get_custo_total()
        visitados = len(grafo_dfs.movimentos.visitados)
        print(f"   Caminho DFS: {' -> '.join(caminho)} (custo: {custo_total}, visitados: {visitados})")
    else:
        print(f"   DFS: Caminho não encontrado de {origem} para {destino}")
    
    # Teste Greedy Best-First Search (GBFS)
    print("\n3. Testando Greedy Best-First Search (GBFS)")
    grafo_gbfs = GrafoGananciosa()
    grafo_gbfs.carregar_json(arquivo_grafo)
    
    if grafo_gbfs.encontrar_caminho(origem, destino):
        caminho = grafo_gbfs.movimentos.get_caminho_completo()
        custo_total = grafo_gbfs.movimentos.get_custo_total()
        visitados = len(grafo_gbfs.movimentos.visitados)
        print(f"   Caminho GBFS: {' -> '.join(caminho)} (custo: {custo_total}, visitados: {visitados})")
        
        # Mostra algumas heurísticas usadas
        print(f"   Heurísticas utilizadas:")
        for no in caminho[:3]:  # Primeiros 3 nós
            h_value = grafo_gbfs._calcular_heuristica(no, destino)
            print(f"     h({no},{destino}) = {h_value}")
    else:
        print(f"   GBFS: Caminho não encontrado de {origem} para {destino}")
    
    print("\n=== Comparação com grafo simples (A -> J) ===")
    arquivo_simples = "base_grafos/grafo_simples.json"
    
    algoritmos = [
        (GrafoBFS, "BFS"),
        (GrafoDFS, "DFS"), 
        (GrafoGananciosa, "GBFS")
    ]
    
    for classe_grafo, nome in algoritmos:
        grafo = classe_grafo()
        grafo.carregar_json(arquivo_simples)
        
        if grafo.encontrar_caminho('A', 'J'):
            caminho = grafo.movimentos.get_caminho_completo()
            custo = grafo.movimentos.get_custo_total()
            visitados = len(grafo.movimentos.visitados)
            print(f"{nome:4}: {' -> '.join(caminho)} (custo: {custo}, visitados: {visitados})")
        else:
            print(f"{nome:4}: Caminho não encontrado")
    
    print("\n=== Testes concluídos ===")
    print("GBFS agora usa fila de prioridade ordenada por heurística")
    print("com backtracking automático (não trava em mínimos locais)")