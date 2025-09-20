from util_grafos import GrafosBase
from collections import deque

class GrafoBFS(GrafosBase):
    """Implementa o algoritmo BFS (Busca em Largura) para encontrar um caminho
       entre dois nós, explorando nível por nível.
    """
    def __init__(self, nome_grafo="Grafo BFS"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'BFS'

    def encontrar_caminho(self, inicio, fim):
        """Implementa o algoritmo BFS (Busca em Largura) para encontrar um caminho
           entre dois nós.
        Args:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
        Returns:
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
    """Implementa o algoritmo DFS (Busca em Profundidade) para encontrar um caminho
       entre dois nós, explorando o máximo possível antes de retroceder.
    """
    def __init__(self, nome_grafo="Grafo DFS"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'DFS'

    def encontrar_caminho(self, inicio, fim):
        """Implementa o algoritmo DFS (Busca em Profundidade) para encontrar um caminho
           entre dois nós.
        Args:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
        Returns:
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
    """Implementa o algoritmo de Busca Gananciosa (Greedy Search) para encontrar um caminho
       entre dois nós, sempre escolhendo o vizinho com menor custo de aresta (decisão gulosa local).
    """
    def __init__(self, nome_grafo="Grafo Busca Gananciosa"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'Gananciosa'

    def encontrar_caminho(self, inicio, fim):
        """Implementa o algoritmo de Busca Gananciosa para encontrar um caminho
           entre dois nós, sempre escolhendo o vizinho com menor custo de aresta.
        Args:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
        Returns:
            bool: True se encontrou caminho, False caso contrário
        """
        # PASSO 1: Preparação inicial
        # Limpa registros de movimentos anteriores
        self.movimentos.reset()
        
        # Verifica se os pontos de início e fim existem no grafo
        if inicio not in self.nos or fim not in self.nos:
            return False
        
        # PASSO 2: Configuração das estruturas de dados da Busca Gananciosa
        # Caminho atual sendo construído
        caminho = [inicio]
        # Conjunto de nós já visitados para evitar ciclos
        visitados = set([inicio])
        # Nó atual da busca
        no_atual = inicio
        # Registra o nó inicial como visitado
        self.movimentos.marcar_visitado(inicio)
        
        # PASSO 3: Loop principal - busca gananciosa
        while no_atual != fim:
            # PASSO 3.1: Obtém todos os vizinhos não visitados
            vizinhos_disponiveis = []
            for vizinho, custo_aresta in self._adjacentes_de(no_atual):
                if vizinho not in visitados:
                    # Armazena vizinho e custo da aresta (estratégia gananciosa por custo)
                    vizinhos_disponiveis.append((vizinho, custo_aresta))
            
            # PASSO 3.2: Se não há vizinhos disponíveis, não há caminho
            if not vizinhos_disponiveis:
                return False
            
            # PASSO 3.3: Escolhe o vizinho com menor custo de aresta (estratégia gananciosa)
            # Ordena por custo da aresta (menor custo = escolha gananciosa)
            vizinhos_disponiveis.sort(key=lambda x: x[1])
            melhor_vizinho, _ = vizinhos_disponiveis[0]
            
            # PASSO 3.4: Move para o melhor vizinho
            caminho.append(melhor_vizinho)
            visitados.add(melhor_vizinho)
            # Registra o nó como visitado no sistema de movimentos
            self.movimentos.marcar_visitado(melhor_vizinho)
            no_atual = melhor_vizinho
        
        # PASSO 4: Registra o caminho encontrado
        for nodo in caminho:
            self.movimentos.mover_para(nodo)
        
        return True


if __name__ == "__main__":
    # Teste das três implementações
    print("=== Testando algoritmos de busca ===\n")
    
    # Carrega o grafo de exemplo
    arquivo_grafo = "base_grafos/grafo_simples.json"
    origem, destino = 'A', 'E'
    
    # Teste BFS
    print("1. Testando BFS (Busca em Largura)")
    grafo_bfs = GrafoBFS()
    grafo_bfs.carregar_json(arquivo_grafo)
    
    if grafo_bfs.encontrar_caminho(origem, destino):
        caminho = grafo_bfs.movimentos.get_caminho_completo()
        custo_total = grafo_bfs.movimentos.get_custo_total()
        print(f"   Caminho BFS: {' -> '.join(caminho)} (custo: {custo_total})")
    else:
        print(f"   BFS: Caminho não encontrado de {origem} para {destino}")
    
    # Teste DFS
    print("\n2. Testando DFS (Busca em Profundidade)")
    grafo_dfs = GrafoDFS()
    grafo_dfs.carregar_json(arquivo_grafo)
    
    if grafo_dfs.encontrar_caminho(origem, destino):
        caminho = grafo_dfs.movimentos.get_caminho_completo()
        custo_total = grafo_dfs.movimentos.get_custo_total()
        print(f"   Caminho DFS: {' -> '.join(caminho)} (custo: {custo_total})")
    else:
        print(f"   DFS: Caminho não encontrado de {origem} para {destino}")
    
    # Teste Busca Gananciosa
    print("\n3. Testando Busca Gananciosa")
    grafo_gan = GrafoGananciosa()
    grafo_gan.carregar_json(arquivo_grafo)
    
    if grafo_gan.encontrar_caminho(origem, destino):
        caminho = grafo_gan.movimentos.get_caminho_completo()
        custo_total = grafo_gan.movimentos.get_custo_total()
        print(f"   Caminho Gananciosa: {' -> '.join(caminho)} (custo: {custo_total})")
    else:
        print(f"   Gananciosa: Caminho não encontrado de {origem} para {destino}")
    
    print("\n=== Testes concluídos ===")