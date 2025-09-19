import time
import sys
import json
from dataclasses import dataclass
from typing import Union

@dataclass
class No():
    letra: str
    label: str = None
    def copy(self):
        return No(
            letra=self.letra,
            label=self.label,
        )

class GrafosBase:
    ''' Estrutura base de grafos com suporte a labels e registro de métricas
        Recebe um nome de grafo e o número de vértices é dinâmico a partir da carga de um 
        arquivo ou da construção manual.
    '''
    def __init__(self, nome_grafo:str = 'Grafo de teste', descricao:str = None):
        self.nome = 'Base'
        self.nome_grafo = nome_grafo
        self.descricao = descricao or nome_grafo
        self.metrica = 'custo'
        self.metrica_final = 'custo total'
        self.adjacentes = []  # guarda a matriz de adjacência [('A', 'B', valor), ('A','C', valor)]
        self.custos = None  # guarda os nós visitados , o nó anterior e o custo
        self.nos = {}  # Dicionário para armazenar objetos No {letra: No}
        self.movimentos = RegistroVisitas(self)  # Sistema de registro de visitas
        
    def __reset(self):
        self.adjacentes = []
        self.custos = None
        self.nos = {}
        self.movimentos = RegistroVisitas(self)
        
    def criar_no(self, no:No, adjacentes_dict: dict = None):
        """Cria ou atualiza um nó
           adjacentes_dict: dicionário de arestas {vértice: peso, ...}
           Um nó só pode ter adjacentes se já existir no grafo o nó adjacente
           Dessa forma, a ordem de criação dos nós importa
           retorna o Nó criado ou atualizado
        """
        # verifica se já existe o nó e substitui
        if no.letra in self.nos:
            self.nos[no.letra] = no.copy()
        else:
            self.nos[no.letra] = no.copy()
        
        # remove apenas as adjacências que partem deste nó (não as que chegam)
        self.adjacentes = [(a, b, c) for a, b, c in self.adjacentes if a != no.letra]

        # recria ou cria os vértices
        if adjacentes_dict:
            for destino, peso in adjacentes_dict.items():
                # Adiciona nova aresta
                destino = str(destino).upper()
                assert destino in self.nos, f"Nó destino '{destino}' não existe. Crie-o antes de adicionar adjacente."  
                self.adjacentes.append((no.letra, destino, peso))
        return self.nos[no.letra]
        
    def _get_no(self, no: Union[str, No]):
        """Retorna o objeto No para uma letra"""
        if no is None:
            return None
        return self.nos.get(no) if isinstance(no, str) else self.nos.get(no.letra)
        
    def set_label(self, no, label):
        """Define um label para um nó específico"""
        no = self._get_no(no)
        if no:
           no.label = label
    
    def get_label(self, no):
        no = self._get_no(no)
        if no:
            return no.label
        return None 
            
    def get_no_por_label(self, label):
        """Encontra um nó pelo seu label"""
        for no in self.nos.values():
            if no.label == label:
                return no
        return None
    
    def get_all_labels(self):
        """Retorna todos os labels em formato {índice: label}"""
        result = {}
        for letra, no in self.nos.items():
            result[letra] = no.label if no.label else letra
        return result

    def __len__(self):
        return len(self.nos)

    def carregar(self, grafo):
        ''' carrega um grafo a partir de um dicionário de nós
            formato: {'A': {'label': 'Centro', 'B':1, 'C': 5}, 'B': {'label': 'Shopping', 'A':1, 'D':3}, ...}
            
            A carga é feita em duas fases:
            1. Primeira fase: cria todos os nós (com labels se existirem)
            2. Segunda fase: cria as adjacências (todos os nós já existem para validação)
        '''
        assert isinstance(grafo, dict), "Use apenas o formato dicionário para a chave 'grafo'"
        self._GrafosBase__reset()
        # Primeira fase: criar todos os nós
        # nõs não se repetem por serem chaves do dicionário
        for letra, dados_no in grafo.items():
            assert isinstance(dados_no, dict), "Os dados do nó devem ser um dicionário"
            letra = str(letra).upper()
            # Extrai o label se existir
            label = None
            if 'label' in dados_no:
                label = dados_no['label']

            # Cria o nó sem adjacentes
            no = No(letra=letra, label=label)
            self.nos[letra] = no
        
        # Segunda fase: criar as adjacências
        # Agora não remove adjacências antigas, apenas adiciona as novas
        for letra, dados_no in sorted(grafo.items(), key=lambda x: x[0]):
            letra = str(letra).upper()
            
            # Adiciona as adjacências
            for destino, peso in dados_no.items():
                if destino == 'label':
                    continue
                destino = str(destino).upper()
                assert destino in self.nos, f"Nó destino '{destino}' não existe. Todos os nós devem estar definidos no grafo."
                
                # Verifica se a aresta já existe para evitar duplicatas
                aresta_existe = False
                for origem_existente, destino_existente, _ in self.adjacentes:
                    if origem_existente == letra and destino_existente == destino:
                        aresta_existe = True
                        break
                
                if not aresta_existe:
                    self.adjacentes.append((letra, destino, peso))

    def carregar_json(self, arquivo_json):
        """Carrega um grafo de um arquivo JSON"""
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                        
            # Carrega o grafo
            self.carregar(dados['grafo'])
            
            # Carrega metadados se existirem
            if 'metrica' in dados:
                self.metrica = dados['metrica']
            if 'metrica_final' in dados:
                self.metrica_final = dados['metrica_final']
            if 'nome_grafo' in dados:
                self.nome_grafo = dados['nome_grafo']
            if 'descricao' in dados:
                self.descricao = dados['descricao']
            
            # Retorna metadados se existirem
            metadados = {k: v for k, v in dados.items() if k != 'grafo'}
            return metadados
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo {arquivo_json} não encontrado")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            raise Exception(f"Erro ao carregar grafo: {e}")

    def mover_para(self, letra:str):
        """Registra a visita de um nó pela letra"""
        self.movimentos.mover_para(letra)

    def percorrer_caminho(self, caminho):
        """
        Percorre um caminho específico registrando todos os movimentos e custos
        
        Args:
            caminho: Lista de nós a serem percorridos
            
        Returns:
            dict: Informações sobre o percurso (custo total, movimentos, etc.)
        """
        self.movimentos.reset()
        
        if not caminho:
            return {'custo_total': 0, 'movimentos': 0, 'sucesso': False}
        
        # Verifica se todos os nós do caminho existem
        for no in caminho:
            if no not in self.nos:
                return {
                    'custo_total': 0, 
                    'movimentos': 0, 
                    'sucesso': False,
                    'erro': f"Nó '{no}' não existe no grafo"
                }
        
        # Percorre todos os nós
        for i, no in enumerate(caminho):
            self.movimentos.mover_para(no)
        
        stats = self.movimentos.get_estatisticas()
        return {
            'custo_total': stats['custo_total'],
            'movimentos': stats['movimentos_totais'],
            'sucesso': True,
            'estatisticas': stats
        }

    def get_registro_visitas(self):
        """Retorna o objeto de registro de visitas"""
        return self.movimentos

    def resetar_visitas(self):
        """Reseta o sistema de visitas"""
        self.movimentos.reset()

    def get_nos_visitados(self):
        """Retorna os nós visitados em formato letras"""
        return list(sorted(self.movimentos.visitados))

    def get_nos_visitados_letras(self):
        """Retorna os nós visitados em formato letras"""
        return list(sorted(self.movimentos.visitados))

    def limpar_visitas(self):
        """Limpa o registro de visitas"""
        self.movimentos.reset()

    def _adjacentes_de(self, u):
        ''' retorna as tuplas de adjacentes para u
           (nó destino, custo)
        '''
        res = []
        for origem, destino, peso in self.adjacentes:
            if origem == u:
                res.append((destino, peso))
        return res

    def print(self, espacos=5):
        """Imprime o grafo em formato de matriz"""
        # Obtém todas as letras dos nós
        letras = sorted(self.nos.keys())
        
        # Cabeçalho
        print(' '.ljust(espacos), ''.join(letra.rjust(espacos) for letra in letras))
        
        # Linhas da matriz
        for letra_origem in letras:
            linha = [letra_origem.ljust(espacos)]
            
            for letra_destino in letras:
                # Busca peso da aresta
                peso = None
                for origem, destino, p in self.adjacentes:
                    if origem == letra_origem and destino == letra_destino:
                        peso = p
                        break
                linha.append(str(peso or '').rjust(espacos))
            
            print(''.join(linha))

class GrafosDijkstra(GrafosBase):
    def __init__(self, nome_grafo:str = 'Grafo Dijkstra', descricao:str = None):
        super().__init__(nome_grafo, descricao)
        self.nome = 'Dijkstra'

    def caminho(self, inicio, fim):
        """Encontra o menor caminho entre dois nós"""
        self.mover_para(inicio) # inicia os contadores
        no_fim, custo, anterior = self.dijkstra(inicio, fim)
        
        # Reconstrói o caminho
        caminho = []
        no_atual = fim
        while no_atual is not None:
            caminho.append(no_atual)
            # Usa a informação anterior dos custos
            if no_atual in self.custos:
                no_atual = self.custos[no_atual][2]  # índice 2 é o anterior
            else:
                break
        caminho.reverse()
        # realiza o caminho encontrado
        for no in caminho[1:]:  # pula o primeiro que é o início
            self.movimentos.mover_para(no)

        return caminho, custo

    def dijkstra(self, inicio, fim):
        """Implementa o algoritmo de Dijkstra"""
        # Passo 1: Inicializar distâncias - início com custo 0, demais com infinito
        self.custos = {}
        for letra in self.nos.keys():
            if letra == inicio:
                self.custos[letra] = (letra, 0, None)  # (nó, custo, anterior)
            else:
                self.custos[letra] = (letra, float('inf'), None)
        
        # Passo 2: Criar fila de prioridade e conjunto de visitados
        fila = [inicio]
        visitados = set()
        
        # Passo 3: Processar nós até fila vazia
        while fila:
            # Passo 4: Selecionar nó com menor distância da fila
            fila.sort(key=lambda x: self.custos[x][1])
            no_atual = fila.pop(0)
            
            # Passo 5: Pular se nó já foi visitado
            if no_atual in visitados:
                continue
                
            # Passo 6: Marcar nó atual como visitado
            visitados.add(no_atual)
            custo_atual = self.custos[no_atual][1]
            
            # Passo 7: Parar se chegou no destino
            if no_atual == fim:
                break
            
            # Passo 8: Examinar todos os vizinhos não visitados
            adjacentes = self._adjacentes_de(no_atual)
            
            for no_adj, custo_adj in adjacentes:
                if no_adj not in visitados:
                    # Passo 9: Calcular nova distância via nó atual
                    novo_custo = custo_atual + custo_adj
                    
                    # Passo 10: Atualizar se encontrou caminho melhor (relaxamento)
                    if novo_custo < self.custos[no_adj][1]:
                        self.custos[no_adj] = (no_adj, novo_custo, no_atual)
                        
                        # Passo 11: Adicionar vizinho na fila se não estiver
                        if no_adj not in fila:
                            fila.append(no_adj)
        
        # Passo 12: Retornar resultado final para o nó destino
        return self.custos[fim]

class RegistroVisitas:
    """
    Classe para registrar visitas em grafos, incluindo:
    - Caminho percorrido (sequência de nós visitados)
    - Custo acumulado durante o percurso
    - Histórico completo de movimentações
    - Estatísticas de visita com tempo e recursos
    RegistroMovimentos é um atributo de GrafosBase e contém referência para ele.
    """
    def __init__(self, grafo):
        self.grafo = grafo  # Referência ao grafo
        self.reset()
    
    def reset(self):
        """Reinicia todos os registros de visita"""
        self.caminho = []           # Lista de nós visitados
        self.custo_total = 0        # Custo acumulado total
        self.custos_parciais = []   # Lista de custos de cada movimento
        self.visitados = set()      # Set de nós únicos visitados
        self.historico = []         # Lista de (origem, destino, custo, tempo) para cada movimento
        self.posicao_atual = None   # Posição atual no grafo
        self.tempo_inicio = time.time()  # Tempo de início
        self.tempo_ultimo_movimento = None  # Tempo do último movimento
        self.tempos_movimentos = []  # Tempos de cada movimento
        self.iteracoes = 0          # Contador de iterações/movimentos
        self.nos_expandidos = 0     # Número de nós expandidos (visitados)
        self.memoria_usada = 0      # Estimativa de uso de memória
    
    def mover_para(self, letra:str):
        """
        Move para uma posição específica registrando o movimento
        Se não houver visitas anteriores, este será o ponto de partida
        
        Args:
            letra: Letra do nó (A, B, C, ...)
        """
        assert self.grafo is not None, "RegistroVisitas requer referência a um grafo"
        assert isinstance(letra, str), "Use apenas letras para nós (A, B, C, ...)"
        letra = letra.upper()
        tempo_atual = time.time()
        
        # Se não há posição atual, este é o ponto de partida
        if self.posicao_atual is None:
            self.caminho.append(letra)
            self.custos_parciais.append(0)  # Custo zero para ponto de partida
            self.posicao_atual = letra
            self.posicao_inicial = letra
            self.tempo_ultimo_movimento = tempo_atual
            self.nos_expandidos = 1
            self.visitados.add(letra)
            # Registra no histórico como ponto de partida
            self.historico.append((None, letra, 0, tempo_atual - self.tempo_inicio))
        else:
            # Movimento normal de uma posição para outra
            origem = self.posicao_atual
            tempo_movimento = (tempo_atual - self.tempo_ultimo_movimento
                               if self.tempo_ultimo_movimento else 0)

            # Busca o custo do movimento na lista de adjacentes
            custo_movimento = None
            for a, b, custo in self.grafo.adjacentes:
                if a == origem and b == letra:
                    custo_movimento = custo
                    break
            
            if custo_movimento is None:
                print(f"Aviso: Não existe aresta entre {origem} e {letra}, usando custo 0")
                custo_movimento = 0
            
            self.caminho.append(letra)
            self.custo_total += custo_movimento
            self.custos_parciais.append(custo_movimento)
            self.tempos_movimentos.append(tempo_movimento)
            self.posicao_atual = letra
            self.tempo_ultimo_movimento = tempo_atual
            self.iteracoes += 1
            
            if letra not in self.visitados:
                self.visitados.add(letra)
                self.nos_expandidos += 1
            
            # Registra no histórico
            self.historico.append((origem, letra, custo_movimento, tempo_movimento))
        
        # Atualiza estimativa de memória (aproximada)
        self.memoria_usada = (sys.getsizeof(self.caminho) +
                              sys.getsizeof(self.visitados) +
                              sys.getsizeof(self.historico) +
                              sys.getsizeof(self.custos_parciais) +
                              sys.getsizeof(self.tempos_movimentos))
    
    def foi_visitado(self, no):
        """Verifica se um nó foi visitado"""
        no = self.grafo._get_no(no)
        if no is None:
            return False
        return bool(no.letra in self.visitados)
    
    def get_caminho_completo(self, letras = True):
        """Retorna o caminho completo percorrido"""
        if letras:
            return self.caminho.copy()
        return [self.grafo._get_no(letra) for letra in self.caminho if self.grafo._get_no(letra)]
    
    def get_custo_total(self):
        """Retorna o custo total acumulado"""
        return self.custo_total
    
    def get_estatisticas(self):
        """
        Retorna estatísticas completas do percurso incluindo métricas de performance
        
        Returns:
            dict: Dicionário com estatísticas
        """
        tempo_total = time.time() - self.tempo_inicio
        tempo_medio_movimento = (sum(self.tempos_movimentos) / len(self.tempos_movimentos)
                                 if self.tempos_movimentos else 0)
        
        return {
            'posicao_inicial': self.posicao_inicial,
            'posicao_atual': self.posicao_atual,
            'nos_visitados': len(self.visitados),
            'nos_unicos': len(self.visitados),
            'movimentos_totais': len(self.caminho) - 1 if len(self.caminho) > 0 else 0,
            'custo_total': self.custo_total,
            'custo_medio_movimento': (self.custo_total / max(1, len(self.custos_parciais) - 1)
                                      if len(self.custos_parciais) > 1 else 0),
            'tempo_total': tempo_total,
            'tempo_medio_movimento': tempo_medio_movimento,
            'iteracoes': self.iteracoes,
            'nos_expandidos': self.nos_expandidos,
            'memoria_usada_bytes': self.memoria_usada,
            # nós por KB
            'eficiencia_memoria': (len(self.visitados) /
                                   max(1, self.memoria_usada / 1024))
        }
    
    def get_historico_movimentos(self, letras = True):
        """Retorna o histórico completo de movimentos"""
        # histórico é (origem, destino, custo, tempo)
        if letras:
            return self.historico.copy()
        return [(self.grafo._get_no(origem) if origem else None,
                 self.grafo._get_no(destino),
                 custo, tempo)
                for origem, destino, custo, tempo in self.historico]
    
    def caminho_descrito(self):
        # retorna o custo dos movimentos letra(label) - [custo] -> letra(label)
        caminho_str = ''
        for i, (letra, custo) in enumerate(zip(self.caminho, self.custos_parciais)):
            no = self.grafo._get_no(letra)
            label = no.label if no and no.label else letra
            _desc = f'{letra}({label})' if letra != label else letra
            if i == 0:
                # Primeiro nó (ponto de partida)
                caminho_str += _desc
            else:
                # Nós subsequentes com custo da aresta
                caminho_str += f" -[{custo}]-> {_desc}"
        
        if not caminho_str:
            caminho_str = 'Nenhum'
        return caminho_str        
    
    def __str__(self):
        """Representação string do registro com informações de performance"""
        stats = self.get_estatisticas()
        
        # Retorna o caminho com labels se disponíveis
        
        return (f"Registro de Visitas:\n"
                f"  Caminho: {self.caminho_descrito()}\n"
                f"  Custo Total: {stats['custo_total']}\n"
                f"  Nós Visitados: {stats['nos_visitados']}\n"
                f"  Movimentos: {stats['movimentos_totais']}\n"
                f"  Tempo Total: {stats['tempo_total']:.3f}s\n"
                f"  Iterações: {stats['iteracoes']}\n"
                f"  Memória: {stats['memoria_usada_bytes']} bytes")


if __name__ == "__main__":
    print("=== Teste simples da classe ===\n")
    
    # Cria um grafo Dijkstra
    grafo = GrafosDijkstra("Teste de Validação")
    
    # Carrega o grafo simples
    try:
        metadados = grafo.carregar_json('base_grafos/grafo_simples.json')
        print(f"Grafo carregado: {grafo.nome_grafo}")
        print(f"Descrição: {grafo.descricao}")
        print(f"Métrica: {grafo.metrica}")
        print(f"Número de nós: {len(grafo)}")
        print(f"Número de adjacências: {len(grafo.adjacentes)}\n")
        
        # Debug: mostra algumas adjacências para verificar se foram carregadas
        print("Primeiras 10 adjacências carregadas:")
        for i, (origem, destino, peso) in enumerate(grafo.adjacentes[:10]):
            print(f"  {origem} -> {destino}: {peso} {grafo.metrica}")
        if len(grafo.adjacentes) > 10:
            print(f"  ... e mais {len(grafo.adjacentes) - 10} adjacências")
        print()
        
        # Mostra os labels dos nós
        print("Nós e seus labels:")
        for letra, no in sorted(grafo.nos.items()):
            adjacentes_do_no = grafo._adjacentes_de(letra)
            print(f"  {letra}: {no.label} (adjacentes: {len(adjacentes_do_no)})")
        print()
        
        # Imprime matriz de adjacência
        print("Matriz de adjacência:")
        grafo.print()
        print()
        
        # Exemplo 1: Encontra menor caminho
        origem, destino = 'A', 'J'
        print(f"=== Exemplo 1: Menor caminho de {origem} para {destino} ===")
        caminho, custo = grafo.caminho(origem, destino)
        print(f"Caminho encontrado: {' -> '.join(caminho)}")
        print(f"Custo total: {custo} {grafo.metrica}")
        
        # Validação: verifica se o custo está correto
        if custo == 0:
            print("⚠️  PROBLEMA: Custo 0 detectado! Verificando adjacências...")
            print(f"Adjacentes de {origem}: {grafo._adjacentes_de(origem)}")
            print(f"Total de adjacências no grafo: {len(grafo.adjacentes)}")
        else:
            print("✅ Custo calculado corretamente!")
        
        # Simula o percurso do caminho encontrado
        resultado = grafo.percorrer_caminho(caminho)
        print(f"Resultado da simulação: {resultado['sucesso']}")
        print(f"Custo simulado: {resultado['custo_total']} {grafo.metrica}")
        print()
        
        # Exemplo 2: Movimento manual no grafo
        print("=== Exemplo 2: Movimento manual no grafo ===")
        grafo.resetar_visitas()
        
        # Faz alguns movimentos manuais
        movimentos_manuais = ['A', 'B', 'C', 'F', 'I', 'J']
        print(f"Movimentos manuais: {' -> '.join(movimentos_manuais)}")
        
        for no in movimentos_manuais:
            grafo.mover_para(no)
            time.sleep(0.01)  # Pequena pausa para simular tempo
        
        print()
        
        # Exemplo 3: Print do resumo final
        print("=== Resumo Final ===")
        registro = grafo.get_registro_visitas()
        print(registro)
        print()
        
        # Estatísticas detalhadas
        stats = registro.get_estatisticas()
        print("Estatísticas detalhadas:")
        for chave, valor in stats.items():
            if isinstance(valor, float):
                print(f"  {chave}: {valor:.3f}")
            else:
                print(f"  {chave}: {valor}")
        print()
        
        # Histórico de movimentos
        print("Histórico de movimentos:")
        historico = registro.get_historico_movimentos()
        for i, (origem, destino, custo, tempo) in enumerate(historico):
            if origem is None:
                print(f"  {i+1}. Início em {destino} (custo: {custo})")
            else:
                print(f"  {i+1}. {origem} -> {destino} (custo: {custo}, tempo: {tempo:.3f}s)")
        
        # Teste adicional: verifica alguns caminhos específicos
        print("\n=== Testes Adicionais de Validação ===")
        testes = [('A', 'B'), ('B', 'C'), ('C', 'F'), ('A', 'E')]
        for orig, dest in testes:
            try:
                cam, cust = grafo.caminho(orig, dest)
                print(f"{orig} -> {dest}: {' -> '.join(cam)} (custo: {cust})")
            except Exception as e:
                print(f"{orig} -> {dest}: ERRO - {e}")
        
    except Exception as e:
        print(f"Erro ao executar exemplo: {e}")
        print("Certifique-se de que o arquivo base_grafos/grafo_simples.json existe")
        import traceback
        traceback.print_exc()
