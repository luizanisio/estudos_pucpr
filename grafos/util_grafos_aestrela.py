from util_grafos import GrafosBase
import heapq

class GrafoAEstrela(GrafosBase):
    def __init__(self, nome_grafo="Grafo A*"):
        super().__init__(nome_grafo=nome_grafo)
        self.nome = 'A*'
        

    def encontrar_caminho(self, inicio, fim):
        """Implementa o algoritmo A* (A-estrela) para encontrar o caminho mais
           curto entre dois nós em um grafo ponderado.
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
        
        # PASSO 2: Configuração das estruturas de dados do A*
        # Lista de nós para explorar (ordenada por prioridade)
        conjunto_aberto = []  # Heap priority queue
        # Conjunto de nós já analisados completamente
        conjunto_fechado = set()  # Nós já processados
        
        # PASSO 3: Inicialização dos custos
        # g_score: custo real percorrido do início até cada nó
        g_score = {no: float('inf') for no in self.nos}  # Custo real do início até o nó
        # f_score: custo estimado total (custo real + estimativa até o fim)
        f_score = {no: float('inf') for no in self.nos}  # g_score + heurística
        # predecessores: para lembrar de onde veio cada nó (reconstruir caminho)
        predecessores = {}  # Para reconstruir o caminho
        
        # PASSO 4: Configuração inicial do ponto de partida
        # O custo para chegar ao início é zero
        g_score[inicio] = 0
        # O custo estimado total é só a heurística (distância estimada até o fim)
        f_score[inicio] = self._heuristica(inicio, fim)
        
        # PASSO 5: Coloca o ponto inicial na lista de nós para explorar
        # Adiciona nó inicial à fila de prioridade
        heapq.heappush(conjunto_aberto, (f_score[inicio], inicio))
        
        # PASSO 6: Loop principal - explora nós até encontrar o destino
        while conjunto_aberto:
            # PASSO 6.1: Pega o nó mais promissor (menor custo estimado total)
            # Pega o nó com menor f_score
            _, no_atual = heapq.heappop(conjunto_aberto)
            
            # PASSO 6.2: Evita processar o mesmo nó duas vezes
            # Se já foi processado, pula
            if no_atual in conjunto_fechado:
                continue
                
            # PASSO 6.3: Marca o nó como completamente analisado
            # Adiciona ao conjunto fechado
            conjunto_fechado.add(no_atual)
            # Registra o nó como visitado no sistema de movimentos
            self.movimentos.marcar_visitado(no_atual)
            
            # PASSO 6.4: Verifica se chegou no destino
            # Se chegou no destino, reconstrói o caminho
            if no_atual == fim:
                caminho_encontrado = self._reconstruir_caminho(predecessores, fim)
                # Registra o caminho no sistema de movimentos
                for nodo in caminho_encontrado:
                    self.movimentos.mover_para(nodo)
                return True
            
            # PASSO 6.5: Explora todos os vizinhos do nó atual
            # Examina todos os vizinhos
            for vizinho, custo_aresta in self._adjacentes_de(no_atual):
                # PASSO 6.6: Ignora vizinhos já completamente processados
                if vizinho in conjunto_fechado:
                    continue
                
                # PASSO 6.7: Calcula o custo para chegar ao vizinho passando pelo nó atual
                # Calcula novo g_score
                g_tentativo = g_score[no_atual] + custo_aresta
                
                # PASSO 6.8: Se encontrou um caminho melhor para o vizinho
                # Se encontrou caminho melhor para o vizinho
                if g_tentativo < g_score[vizinho]:
                    # PASSO 6.9: Atualiza as informações do vizinho
                    # Lembra de onde veio (para reconstruir o caminho depois)
                    predecessores[vizinho] = no_atual
                    # Atualiza o custo real para chegar até ele
                    g_score[vizinho] = g_tentativo
                    # Atualiza o custo estimado total (real + estimativa até o fim)
                    f_score[vizinho] = g_tentativo + self._heuristica(vizinho, fim)
                    
                    # PASSO 6.10: Coloca o vizinho na lista para ser explorado
                    # Adiciona à fila se não está lá
                    heapq.heappush(conjunto_aberto, (f_score[vizinho], vizinho))
        
        # PASSO 7: Se chegou aqui, não existe caminho
        # Não encontrou caminho
        return False

    def _reconstruir_caminho(self, predecessores, no_final):
        """Reconstrói o caminho a partir dos predecessores
        
        Funciona como uma trilha de migalhas: a partir do destino,
        segue os predecessores até chegar no início.
        
        Args:
            predecessores: Dicionário de predecessores
            no_final: Nó final do caminho
            
        Returns:
            list: Lista de nós formando o caminho
        """
        # PASSO 1: Inicia uma lista vazia para o caminho
        lista_caminho = []
        no_atual = no_final
        
        # PASSO 2: Vai voltando pelo caminho, seguindo os predecessores
        while no_atual is not None:
            # Adiciona o nó atual na frente da lista
            lista_caminho.append(no_atual)
            # Vai para o nó anterior (predecessor)
            no_atual = predecessores.get(no_atual)
        
        # PASSO 3: Inverte a lista para ficar na ordem correta (início -> fim)
        # Inverte para ficar na ordem correta (início -> fim)
        lista_caminho.reverse()
        return lista_caminho
    
if __name__ == "__main__":
    # Teste simples do GrafoAEstrela
    grafo = GrafoAEstrela()
    grafo.carregar_json("base_grafos/grafo_acai.json")

    origem, destino = 'A', 'J'
    print(f"Testando A* de {origem} para {destino}")
    encontrou_caminho = grafo.encontrar_caminho(origem, destino)
    
    if encontrou_caminho:
        caminho = grafo.movimentos.get_caminho_completo()
        custo_total = grafo.movimentos.get_custo_total()
        print(f"Caminho encontrado: {' -> '.join(caminho)} com custo {custo_total}")
        print(f'Caminho descrito: {grafo.movimentos.caminho_descrito()}')
        print(f'Caminho heurística vs real: '
              f'{grafo.movimentos.caminho_descrito_heuristica_vs_real()}')
    else:
        print("Caminho não encontrado.")