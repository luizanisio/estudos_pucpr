'''
Classe que implementa a geração do grafo visual com nós visitados e nós do caminho final.
'''

from util_grafos import GrafosDijkstra, RegistroVisitas, GrafosBase
from util_grafos_outros import GrafoBFS, GrafoDFS, GrafoGananciosa
from util_grafos_aestrela import GrafoAEstrela
import os
import re

try:
    from pyvis.network import Network
    PYVIS_OK = True
except ImportError:
    PYVIS_OK = False

def conferir_pyvis():
    """ Verifica se a biblioteca pyvis está instalada. """
    if PYVIS_OK:
        return True
    print("❌ Pyvis não disponível. Instale com: pip install pyvis")
    return False

class VisualizacaoGrafo:
    """ Gera visualizações interativas de grafos com pyvis. """

    def __init__(self, grafo:GrafosBase, titulo="Visualização do Grafo"):
        self.titulo = titulo
        self.grafo = grafo
        self.registro = grafo.movimentos

    def gerar_grafo_visual(self, nome_arquivo=None, origem=None, destino=None):
        """
        Gera o grafo visual com nós visitados e caminho final.
        Parâmetros:
            nome_arquivo: Nome do arquivo de saída (sem extensão)
            origem: Nó de origem do caminho
            destino: Nó de destino do caminho
        Retorna:
            str: Nome do arquivo HTML gerado ou None se ocorrer algum erro
        """
        if not conferir_pyvis():
            return None

        if not self.registro:
            print("❌ Erro: Registro de visitas não fornecido.")
            return None

        try:
            # Gera nome do arquivo se não fornecido
            if not nome_arquivo:
                nome_algoritmo = getattr(self.grafo, 'nome', 'Grafo')
                origem = origem or (self.registro.caminho[0] if self.registro.caminho else 'A')
                destino = destino or (self.registro.caminho[-1] if self.registro.caminho else 'J')
                nome_arquivo = f"grafo_{nome_algoritmo}_{origem}_{destino}"

            # Garante extensão .html
            if not nome_arquivo.endswith('.html'):
                nome_arquivo_html = nome_arquivo + '.html'
            else:
                nome_arquivo_html = nome_arquivo

            # Cria diretório se não existir
            if '/' in nome_arquivo_html:
                diretorio = os.path.dirname(nome_arquivo_html)
                os.makedirs(diretorio, exist_ok=True)

            # Configura a rede
            net = Network(
                height="600px",
                width="100%",
                bgcolor="#f8f9fa",
                font_color="black",
                directed=True
            )
            
            # Configura física da rede
            net.set_options("""
            var options = {
              "layout": { "improvedLayout": true },
              "physics": {
                "enabled": true,
                "stabilization": {"iterations": 2000}
              }
            }
            """)
            
            # Adiciona nós e arestas
            self._adicionar_nos_e_arestas(net)
            
            # Remove título automático do pyvis
            net.heading = self.titulo

            # Salva o arquivo
            net.save_graph(nome_arquivo_html)
            
            #rodapé
            caminho_heuristica = f'Caminho real vs heurística: {self.grafo.movimentos.caminho_descrito_heuristica_vs_real()} <hr>' if isinstance(self.grafo, GrafoAEstrela) else ''
            custo = self.grafo.movimentos.get_custo_total()
            rodape = ( f'Melhor caminho: {self.grafo.movimentos.caminho_descrito()} <hr>' 
                       f'{caminho_heuristica}'
                       f'Visitas: {self.registro.get_caminho_visitas()} <hr>'
                       f'Custo total: {custo:.2f} ')
            self.remover_primeiro_h1_pyvis(nome_arquivo_html,
                                           incluir_rodape=rodape)

            print(f"✅ Grafo visual salvo em: {nome_arquivo_html}")
            return nome_arquivo_html

        except Exception as e:
            print(f"❌ Erro ao gerar grafo visual: {e}")
            raise

    def _adicionar_nos_e_arestas(self, net):
        """ Adiciona nós e arestas à rede com cores distintivas. """
        
        # Obter informações do caminho e visitas
        caminho_final = self.registro.caminho if self.registro.caminho else []
        nos_visitados = list(self.registro.visitados) if self.registro.visitados else []
        
        # Cores para diferentes tipos de nós
        COR_CAMINHO_FINAL = "#28a745"      # Verde
        COR_VISITADO = "#ffc107"           # Amarelo
        COR_NAO_VISITADO = "#6c757d"       # Cinza
        COR_ORIGEM = "#007bff"             # Azul
        COR_DESTINO = "#dc3545"            # Vermelho

        # Adiciona todos os nós do grafo
        for letra, no in self.grafo.nos.items():
            # Determina a cor do nó
            if letra == caminho_final[0] if caminho_final else False:
                cor = COR_ORIGEM
                tamanho = 25
            elif letra == caminho_final[-1] if caminho_final else False:
                cor = COR_DESTINO
                tamanho = 25
            elif letra in caminho_final:
                cor = COR_CAMINHO_FINAL
                tamanho = 20
            elif letra in nos_visitados:
                cor = COR_VISITADO
                tamanho = 15
            else:
                cor = COR_NAO_VISITADO
                tamanho = 10

            # Label do nó
            label_visivel = no.label if no.label else letra
            titulo = f"{letra}: {label_visivel}" if no.label else letra

            # Cor da fonte baseada na cor de fundo
            if cor in [COR_ORIGEM, COR_DESTINO]:
                cor_fonte = 'white'
            else:
                cor_fonte = 'black'

            # Adiciona o nó
            net.add_node(
                letra,
                label=titulo,
                title=titulo,
                color=cor,
                size=tamanho,
                font={'size': 14, 'face': 'arial', 'color': cor_fonte, 'bold': True}
            )
            
            if self.grafo.coordenadas and letra in self.grafo.coordenadas:
                x, y = self.grafo.coordenadas[letra]
                net.nodes[-1]['x'] = x
                net.nodes[-1]['y'] = y
                net.nodes[-1]['fixed'] = {'x': True, 'y': True}

        # Adiciona arestas (evita duplicatas mantendo apenas uma aresta por par de nós)
        arestas_adicionadas = set()
        
        for origem, destino, peso in self.grafo.adjacentes:
            # Cria chave única para o par de nós
            chave_aresta = tuple(sorted([origem, destino]))
            
            # Se já adicionamos esta aresta, pula
            if chave_aresta in arestas_adicionadas:
                continue
            
            # Marca como adicionada
            arestas_adicionadas.add(chave_aresta)
            
            # Determina se a aresta faz parte do caminho
            from_to = ''
            if self._aresta_no_caminho(origem, destino, caminho_final):
                from_to = 'to'
            elif self._aresta_no_caminho(destino, origem, caminho_final):
                from_to = 'from'
            from_to_visitas = ''
            if not from_to:
                if self._aresta_no_caminho(origem, destino, caminho_final, visitas=True):
                    from_to_visitas = 'to'
                elif self._aresta_no_caminho(destino, origem, caminho_final, visitas=True):
                    from_to_visitas = 'from'
            
            # Determina estilo da aresta
            if from_to:
                cor_aresta = "#28a745"
                largura = 4
                tipo_linha = "solid"
                arrows = {f"{from_to}": {"enabled": True, "scaleFactor": 1.2}}
            else:
                cor_aresta = "#6c757d"
                largura = 1
                tipo_linha = "dashed"
                if from_to_visitas:
                    arrows = {f"{from_to_visitas}": {"enabled": True}}
                else:
                    arrows = {"to": {"enabled": False}}

            # Adiciona a aresta
            net.add_edge(
                origem,
                destino,
                label=str(peso),
                title=f"{origem} ↔ {destino}: {peso}",
                color=cor_aresta,
                width=largura,
                dashes=(tipo_linha == "dashed"),
                arrows=arrows
            )

    def _aresta_no_caminho(self, origem, destino, caminho, visitas = False):
        """ Verifica se uma aresta faz parte do caminho final ou das visitas se visitas = True. """
        lista = caminho if not visitas else self.registro.get_caminho_visitas()
        if not lista or len(lista) < 2:
            return False

        for i in range(len(lista) - 1):
            if lista[i] == origem and lista[i + 1] == destino:
                return True
        return False

    def remover_primeiro_h1_pyvis(self, caminho_html: str, incluir_rodape:str):
        """ Remove a primeira ocorrência do título <h1> gerado automaticamente pelo pyvis.
        """
        try:
            # se der erro de encode, tenta sem definir o encode
            with open(caminho_html, 'r', encoding='utf-8') as f:
                html = f.read()
        except Exception:
            with open(caminho_html, 'r') as f:
                html = f.read()
            
        # remove só a 1ª ocorrência do <center><h1>...</h1></center>
        html = re.sub(r'<center>\s*<h1>.*?</h1>\s*</center>', '', html, count=1, flags=re.DOTALL)
        if incluir_rodape:
            rodape = ('<div style="text-align: left;">'
                      f'{incluir_rodape}</div>')
            html = html.replace('</body>', rodape + '</body>')
        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
if __name__ == "__main__":
    print("🎨 Testando Visualização de Grafos")
    print("=" * 50)
    
    algoritmos = [
        GrafoDFS("Grafo DFS - Açaí"),
        GrafoBFS("Grafo BFS - Açaí"),
        GrafoAEstrela("Grafo A* - Açaí"),
        GrafoGananciosa("Grafo Gananciosa - Açaí"),
        GrafosDijkstra("Grafo Dijkstra - Açaí")
    ]
    
    for algoritmo in algoritmos:
        algoritmo.carregar_json('base_grafos/grafo_acai.json')
        encontrou = algoritmo.encontrar_caminho('A', 'J')
        if encontrou:
            viz = VisualizacaoGrafo(algoritmo, titulo=f"Grafo Açaí - {algoritmo.nome}")
            arquivo_nome = f"./resultados/grafo_{algoritmo.nome.lower()}_acai"
            arquivo = viz.gerar_grafo_visual(arquivo_nome, 'A', 'J')
            if arquivo:
                print(f"   - {algoritmo.nome}: {arquivo}")
        else:
            print(f"❌ {algoritmo.nome} não encontrou caminho")
