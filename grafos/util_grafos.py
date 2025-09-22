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
    """ Estrutura base de grafos com suporte a labels e registro de métricas. """
    def __init__(self, nome_grafo:str = 'Grafo de teste', descricao:str = None):
        self.nome = 'Base'
        self.nome_grafo = nome_grafo
        self.descricao = descricao or nome_grafo
        self.metrica = 'custo'
        self.metrica_final = 'custo total'
        self.adjacentes = []  # guarda a matriz de adjacência [('A', 'B', valor), ('A','C', valor)]
        self.nos = {}  # Dicionário para armazenar objetos No {letra: No}
        self.movimentos = RegistroVisitas(self)  # Sistema de registro de visitas
        self.heuristicas = {}  # Dicionário para armazenar heurísticas {(origem, destino): custo_estimado}
        self.coordenadas = None # Coordenadas opcionais para visualização {letra: (x, y)}
        
    def __reset(self):
        self.adjacentes = []
        self.nos = {}
        self.movimentos = RegistroVisitas(self)
        self.heuristicas = {}
        self.coordenadas = None
        
    def criar_no(self, no:No, adjacentes_dict: dict = None):
        """ Cria ou atualiza um nó no grafo. """
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
        """ Retorna o objeto No para uma letra. """
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

    def carregar(self, grafo, coordenadas: dict = None):
        """
        Carrega um grafo a partir de um dicionário de nós.
        
        Parâmetros:
            grafo: Dicionário no formato {'A': {'label': 'Centro', 'B':1, 'C': 5}, ...}
            
        Retorna:
            None
        """
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
            else:
                label = letra  # Usa a letra como label padrão se não houver label

            # Cria o nó sem adjacentes
            no = No(letra=letra, label=label)
            self.nos[letra] = no
        
        self.coordenadas = coordenadas if isinstance(coordenadas, dict) and any(coordenadas) else None
        # Segunda fase: criar as adjacências e heurísticas
        # Agora não remove adjacências antigas, apenas adiciona as novas
        for letra, dados_no in sorted(grafo.items(), key=lambda x: x[0]):
            letra = str(letra).upper()
            
            # Adiciona as adjacências e heurísticas
            for destino, peso in dados_no.items():
                if destino == 'label':
                    continue
                
                destino_str = str(destino).upper()
                
                # Verifica se é uma heurística (formato ~LETRA)
                if destino_str.startswith('~'):
                    # Remove o ~ e armazena como heurística
                    destino_heuristica = destino_str[1:]
                    if destino_heuristica in self.nos:
                        self.heuristicas[(letra, destino_heuristica)] = peso
                    continue
                
                # Adjacência normal
                assert destino_str in self.nos, f"Nó destino '{destino_str}' não existe. Todos os nós devem estar definidos no grafo."
                
                # Verifica se a aresta já existe para evitar duplicatas
                aresta_existe = False
                for origem_existente, destino_existente, _ in self.adjacentes:
                    if origem_existente == letra and destino_existente == destino_str:
                        aresta_existe = True
                        break
                
                if not aresta_existe:
                    self.adjacentes.append((letra, destino_str, peso))

    def carregar_json(self, arquivo_json):
        """
        Carrega um grafo de um arquivo JSON.
        
        Parâmetros:
            arquivo_json: Caminho para o arquivo JSON
            
        Retorna:
            dict: Metadados do arquivo JSON (exceto 'grafo')
        """
        try:
            # tenta carregar utf8 (se der erro de encode, tenta sem definir o encode)
            try:
                with open(arquivo_json, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                with open(arquivo_json, 'r') as f:
                    dados = json.load(f)
                        
            # Carrega o grafo
            self.carregar(dados['grafo'], coordenadas=dados.get('coordenadas', None))
            
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

    def vertice(self, origem: str, destino: str, custo_padrao = float('inf')):
        """Verifica se existe ligação entre origem e destino e 
           retorna origem, destino e custo da ligação ou infinito se não existir
        """
        if origem not in self.nos:
            raise ValueError("Origem não existem no grafo")
        if destino not in self.nos:
            raise ValueError("Destino não existem no grafo")
        
        # Encontra o caminho usando o algoritmo específico
        vertice = [v for v in self.adjacentes if v[0] == origem and v[1] == destino]
        
        if not any(vertice):
           # retorna infinito ou o custo padrão se fornecido 
           return (origem, destino, custo_padrao)   
                
        # origem, destino, custo
        return vertice[0][0], vertice[0][1], vertice[0][2]

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
        """Retorna os nós visitados em formato letras (ordem alfabética)"""
        return list(sorted(self.movimentos.visitados))

    def get_nos_visitados_letras(self):
        """Retorna os nós visitados em formato letras (ordem alfabética)"""
        return list(sorted(self.movimentos.visitados))

    def get_nos_visitados_ordem(self):
        """Retorna os nós visitados na ordem em que foram visitados"""
        return self.movimentos.get_caminho_visitas(letras=True)

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

    def _heuristica(self, origem, destino):
        """Retorna o custo heurístico entre origem e destino
        Args:
            origem: Nó de origem
            destino: Nó de destino
        Returns:
            float: Custo heurístico ou 0 se não existir
        Fallback:
            caso não exista a heurística, retorna 0 (admissível)
        """
        return self.heuristicas.get((origem, destino), 0)

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

    def encontrar_caminho(self, inicio, fim):
        """Aciona o algoritmo e realiza o movimento do caminho encontrado e registra as métricas"""
        raise NotImplementedError("Subclasses devem implementar este método")
    
    def obter_caminho_e_custo(self, inicio, fim):
        """
        Executa encontrar_caminho e retorna tupla (caminho, custo_total)
        
        Args:
            inicio: Nó de origem
            fim: Nó de destino
            
        Returns:
            tuple: (lista_caminho, custo_total)
        """
        # Executa o algoritmo
        sucesso = self.encontrar_caminho(inicio, fim)
        
        if not sucesso:
            return ([], 0)
        
        # Extrai caminho e custo do registro de movimentos
        caminho = self.movimentos.get_caminho_completo()
        custo = self.movimentos.get_custo_total()
        
        return (caminho, custo)

class GrafosDijkstra(GrafosBase):
    """ Implementa o algoritmo de Dijkstra para encontrar o caminho de menor custo. """
    def __init__(self, nome_grafo:str = 'Grafo Dijkstra', descricao:str = None):
        super().__init__(nome_grafo, descricao)
        self.nome = 'Dijkstra'

    def encontrar_caminho(self, inicio, fim):
        """
        Implementa o algoritmo de Dijkstra e registra os movimentos.
        
        Parâmetros:
            inicio: Nó de origem (string)
            fim: Nó de destino (string)
            
        Retorna:
            bool: True se encontrou caminho, False caso contrário
        """
        self.movimentos.reset()
        
        # Inicializa custos
        self.custos = {}
        for letra in self.nos.keys():
            if letra == inicio:
                self.custos[letra] = (letra, 0, None)  # (nó, custo, anterior)
            else:
                self.custos[letra] = (letra, float('inf'), None)
        
        fila = [inicio]
        visitados = set()
        
        while fila:
            # Ordena por custo e pega o menor
            fila.sort(key=lambda x: self.custos[x][1])
            no_atual = fila.pop(0)
            
            if no_atual in visitados:
                continue
                
            visitados.add(no_atual)
            # Registra o nó como visitado no sistema de movimentos
            self.movimentos.marcar_visitado(no_atual)
            custo_atual = self.custos[no_atual][1]
            
            # Se chegou no fim, pode parar
            if no_atual == fim:
                break
            
            # Verifica adjacentes
            adjacentes = self._adjacentes_de(no_atual)
            
            for no_adj, custo_adj in adjacentes:
                if no_adj not in visitados:
                    novo_custo = custo_atual + custo_adj
                    
                    # Se encontrou caminho melhor, atualiza
                    if novo_custo < self.custos[no_adj][1]:
                        self.custos[no_adj] = (no_adj, novo_custo, no_atual)
                        
                        if no_adj not in fila:
                            fila.append(no_adj)
        
        # Reconstrói o caminho usando os custos calculados
        if self.custos[fim][1] == float('inf'):
            # Não há caminho
            return False
        
        # Reconstrói o caminho de trás para frente
        caminho_reconstruido = []
        no_atual = fim
        while no_atual is not None:
            caminho_reconstruido.append(no_atual)
            no_atual = self.custos[no_atual][2]  # anterior
        
        # Inverte para ficar na ordem correta
        caminho_reconstruido.reverse()
        
        # Registra os movimentos no sistema de visitas
        for no in caminho_reconstruido:
            self.movimentos.mover_para(no)
        
        return True

class RegistroVisitas:
    """ Registra visitas em grafos incluindo caminho, custo e estatísticas. """
    def __init__(self, grafo):
        self.grafo = grafo  # Referência ao grafo
        self.reset()
    
    def reset(self):
        """ Reinicia todos os registros de visita. """
        self.caminho = []           # Lista de nós visitados
        self.custo_total = 0        # Custo acumulado total
        self.custos_parciais = []   # Lista de custos de cada movimento
        self.visitados = set()      # Set de nós únicos visitados
        self.visitados_ordem = []   # Lista de nós visitados na ordem das visitas
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
            # Não resetar nos_expandidos! Pode já ter nós marcados durante a busca
            if letra not in self.visitados:
                self.visitados.add(letra)
                self.visitados_ordem.append(letra)
                self.nos_expandidos += 1
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
                self.visitados_ordem.append(letra)
                self.nos_expandidos += 1
            
            # Registra no histórico
            self.historico.append((origem, letra, custo_movimento, tempo_movimento))
        
        # Atualiza estimativa de memória (aproximada)
        self.memoria_usada = (sys.getsizeof(self.caminho) +
                              sys.getsizeof(self.visitados) +
                              sys.getsizeof(self.visitados_ordem) +
                              sys.getsizeof(self.historico) +
                              sys.getsizeof(self.custos_parciais) +
                              sys.getsizeof(self.tempos_movimentos))
    
    def marcar_visitado(self, letra):
        """Marca um nó como visitado sem necessariamente mover para ele.
        Usado para registrar nós explorados durante algoritmos de busca.
        """
        letra = letra.upper()
        if letra not in self.visitados:
            self.visitados.add(letra)
            self.visitados_ordem.append(letra)
            self.nos_expandidos += 1
    
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

    def get_caminho_visitas(self, letras = True):
        """Retorna o caminho das visitas feitas na ordem em que foram visitadas"""
        if letras:
            return self.visitados_ordem.copy()
        return [self.grafo._get_no(letra) for letra in self.visitados_ordem
                if self.grafo._get_no(letra)]
    
    def get_custo_total(self):
        """Retorna o custo total acumulado"""
        return round(self.custo_total, 2)
    
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
    
    def caminho_descrito(self, usar_labels = True):
        # retorna o custo dos movimentos letra(label) - [custo] -> letra(label)
        caminho_str = ''
        for i, (letra, custo) in enumerate(zip(self.caminho, self.custos_parciais)):
            no = self.grafo._get_no(letra)
            label = no.label if no and no.label else letra
            _desc = f'{letra}({label})' if usar_labels and letra != label else letra
            if i == 0:
                # Primeiro nó (ponto de partida)
                caminho_str += _desc
            else:
                # Nós subsequentes com custo da aresta
                caminho_str += f" -[{custo:.2f}]-> {_desc}"
        
        if not caminho_str:
            caminho_str = 'Nenhum'
        return caminho_str
    
    def caminho_descrito_heuristica_vs_real(self, usar_labels = True):
        ''' Retorna uma descrição, passo a passo, do custo real até o final vs custo heurístico
            semelhante à descrição do caminho, mas incluindo a heurística
            A heurística usa o custo real até o próximo vértice + estimativa do próximo ao final
            O custo real é o custo acumulado até o final
            Utiliza os dados já calculados do método caminho_heuristica_vs_real
            Ex. A -> B -> C
              Retorna A -[r:5+3 | h:5+2]-> B -[r:3 | h:2]-> C
        '''
        if not self.historico:
            return 'Nenhum movimento registrado'
        
        # Obtém os dados já calculados
        dados_heuristica_real = self.caminho_heuristica_vs_real()
        
        if not dados_heuristica_real:
            return 'Nenhum movimento registrado'
        
        # Identifica o destino final
        destino_final = self.historico[-1][1]
        
        caminho_str = ''
        
        for i, dados in enumerate(dados_heuristica_real):
            origem, destino, heuristica_ate_final, custo_real_ate_final = dados
            # Obtém o objeto nó para formatar com label
            no_destino = self.grafo._get_no(destino)
            label_destino = no_destino.label if no_destino and no_destino.label else destino
            if usar_labels and destino != label_destino:
                destino_formatado = f"{destino}({label_destino})"
            else:
                destino_formatado = destino
            
            if origem == destino:
                # Ponto de partida (origem == destino)
                caminho_str += destino_formatado
            else:
                # Movimento normal
                # Obtém o custo da aresta atual
                custo_aresta = None
                for orig_hist, dest_hist, custo_hist, _ in self.historico:
                    if orig_hist == origem and dest_hist == destino:
                        custo_aresta = custo_hist
                        break
                
                if custo_aresta is None:
                    custo_aresta = 0
                
                # Calcula os componentes
                if destino == destino_final:
                    # Último movimento - mostra custo da aresta e heurística de origem para destino
                    heuristica_origem_destino = self.grafo._heuristica(origem, destino)
                    caminho_str += (f" -[r:{custo_aresta:.2f} | "
                                   f"h:{heuristica_origem_destino:.2f}]-> {destino_formatado}")
                else:
                    # Movimento intermediário - mostra decomposição
                    heuristica_destino = self.grafo._heuristica(destino, destino_final)
                    caminho_str += (f" -[r:{custo_aresta:.2f}+{custo_real_ate_final:.2f} | "
                                   f"h:{custo_aresta:.2f}+{heuristica_destino:.2f}]-> {destino_formatado}")
        
        return caminho_str
        
        return caminho_str

    def caminho_heuristica_vs_real(self):
        ''' Retorna uma lista de tuplas com os valores de heurística vs real por passo
            Formato: [('A','F',heurística, real), ...]
            Os valores são do ponto atual até o ponto final:
            - heurística = custo real da aresta + heurística do destino ao final
            - real = custo real total restante até o final
            - Para o nó final: custo = 0, heurística = 0 (dele para ele mesmo)
            - Para nó diretamente ligado ao final: real = heurística (ambos iguais ao custo da aresta)
            
            Returns:
                list: Lista de tuplas (origem, destino, heuristica_ate_final, real_ate_final)
        '''
        if not self.historico:
            return []
        
        # Identifica o destino final (último nó do caminho)
        destino_final = self.historico[-1][1]  # último destino do histórico
        
        # Calcula custo total do caminho
        custo_total_caminho = sum(custo for _, _, custo, _ in self.historico if custo > 0)
        
        resultado = []
        custo_acumulado = 0
        
        for i, (origem, destino, custo, _) in enumerate(self.historico):
            if origem is None:
                # Ponto de partida - custo até final é o custo total
                custo_real_ate_final = custo_total_caminho
                
                # No ponto inicial (nó para ele mesmo), heurística é 0
                heuristica_ate_final = 0
                
                resultado.append((destino, destino, heuristica_ate_final, custo_real_ate_final))
                continue
            
            # Atualiza custo acumulado
            custo_acumulado += custo
            
            # Custo real restante até o final
            custo_real_ate_final = custo_total_caminho - custo_acumulado
            
            # Se chegou no destino final, custo restante = 0
            if destino == destino_final:
                # Para o destino final, sempre retorna 0 (heurística dele para ele mesmo)
                heuristica_ate_final = 0
                custo_real_ate_final = 0  # Do final para ele mesmo = 0
            else:
                # Heurística: custo da aresta atual + estimativa do destino ao final
                heuristica_destino_ao_final = self.grafo._heuristica(destino, destino_final)
                # Sempre calcula a heurística, mesmo que seja 0
                heuristica_ate_final = custo + heuristica_destino_ao_final
            
            resultado.append((origem, destino, heuristica_ate_final, custo_real_ate_final))
        
        return resultado
    
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
    from testes.exemplos import get_g_youtube
    
    # Cria um grafo Dijkstra
    grafo = get_g_youtube()
    
    # Testa o grafo carregado
    try:
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
        
        # Exemplo 1: Encontra menor caminho usando o novo método
        origem, destino = 'A', 'C'
        print(f"=== Exemplo 1: Menor caminho de {origem} para {destino} ===")
        print( 'Esperado: A -[2.00]-> B -[1.00]-> E -[3.00]-> C  = 6.00' )
        grafo.encontrar_caminho(origem, destino)
        print(f"Caminho encontrado: {grafo.movimentos.caminho_descrito()}")
        print(f"Custo total: {grafo.movimentos.get_custo_total()} {grafo.metrica}")
        
        # Validação: verifica se o custo está correto
        if grafo.movimentos.get_custo_total() == 0:
            print("⚠️  PROBLEMA: Custo 0 detectado! Verificando adjacências...")
            print(f"Adjacentes de {origem}: {grafo._adjacentes_de(origem)}")
            print(f"Total de adjacências no grafo: {len(grafo.adjacentes)}")
        else:
            print("✅ Custo calculado corretamente!")
        print()
        
        # Exemplo 2: Testando o método percorrer_caminho
        print("=== Exemplo 2: Percorrendo caminho específico ===")
        caminho_teste = ['A', 'D', 'E', 'G', 'C']
        print(f"Caminho para testar: {' -> '.join(caminho_teste)}")
        
        resultado = grafo.percorrer_caminho(caminho_teste)
        print(f"Resultado da simulação: {resultado['sucesso']}")
        print(f"Custo simulado: {resultado['custo_total']} {grafo.metrica}")
        print()
        
        # Exemplo 3: Movimento manual no grafo
        print("=== Exemplo 3: Movimento manual no grafo ===")
        grafo.resetar_visitas()
        
        # Faz alguns movimentos manuais
        movimentos_manuais = ['A', 'D', 'E']
        print(f"Movimentos manuais: {' -> '.join(movimentos_manuais)}")
        
        for no in movimentos_manuais:
            grafo.mover_para(no)
        
        print(f"Caminho percorrido: {grafo.movimentos.caminho_descrito()}")
        print()
        
        # Exemplo 4: Print do resumo final
        print("=== Exemplo 4: Resumo Final ===")
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
        
        # Teste adicional: verifica alguns vértices específicos
        print("\n=== Exemplo 5: Testes de Vértices ===")
        testes = [('A', 'D'), ('E', 'G'), ('A', 'Z')]  # Incluindo um caso de erro
        for orig, dest in testes:
            try:
                origem_ret, destino_ret, custo = grafo.vertice(orig, dest)
                if custo == float('inf'):
                    print(f"{orig} -> {dest}: Não existe ligação direta")
                else:
                    print(f"{orig} -> {dest}: {origem_ret} -> {destino_ret} (custo: {custo})")
            except Exception as e:
                print(f"{orig} -> {dest}: ERRO - {e}")
        
    except Exception as e:
        print(f"Erro ao executar exemplo: {e}")
        print("Certifique-se de que o arquivo util_grafos_exemplos.py existe e contém get_g_youtube()")
        import traceback
        traceback.print_exc()
