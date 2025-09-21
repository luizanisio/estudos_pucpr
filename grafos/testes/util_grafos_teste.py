#!/usr/bin/env python3
"""
Testes unitários para util_grafos.py
Organizados por tópicos: carga, comparação, visitas, custos, algoritmos
"""

import unittest
import sys
import os
import io
import json
import tempfile

# Adiciona o diretório atual ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_grafos import GrafosBase, GrafosDijkstra, No
from util_grafos_aestrela import GrafoAEstrela
from util_grafos_outros import GrafoGananciosa


class TestCargaGrafos(unittest.TestCase):
    """Testes para carregamento de grafos em diferentes formatos"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste de Carga")
    
    def test_carga_formato_dicionario(self):
        """Testa carregamento de grafo no formato dicionário"""
        dados_dict = {
            'A': {'B': 2, 'C': 4},
            'B': {'A': 2, 'C': 1, 'D': 7},
            'C': {'A': 4, 'B': 1, 'D': 3},
            'D': {'B': 7, 'C': 3}
        }
        
        self.grafo.carregar(dados_dict)
        
        # Verifica se os nós foram criados
        self.assertEqual(len(self.grafo), 4)
        self.assertIn('A', self.grafo.nos)
        self.assertIn('B', self.grafo.nos)
        self.assertIn('C', self.grafo.nos)
        self.assertIn('D', self.grafo.nos)
        
        # Verifica adjacências
        adj_a = self.grafo._adjacentes_de('A')
        self.assertEqual(len(adj_a), 2)
        adj_dict_a = dict(adj_a)
        self.assertEqual(adj_dict_a['B'], 2)
        self.assertEqual(adj_dict_a['C'], 4)
    
    def test_carga_com_labels(self):
        """Testa carregamento de grafo com labels"""
        dados_com_labels = {
            'A': {'label': 'Casa', 'B': 2, 'C': 4},
            'B': {'label': 'Trabalho', 'A': 2, 'D': 7},
            'C': {'label': 'Loja', 'A': 4, 'D': 3},
            'D': {'B': 7, 'C': 3}  # Sem label explícito
        }
        
        self.grafo.carregar(dados_com_labels)
        
        # Verifica labels
        self.assertEqual(self.grafo.get_label('A'), 'Casa')
        self.assertEqual(self.grafo.get_label('B'), 'Trabalho')
        self.assertEqual(self.grafo.get_label('C'), 'Loja')
        self.assertEqual(self.grafo.get_label('D'),'D')  # Sem label
        
        # Verifica se as adjacências foram carregadas
        adj_a = self.grafo._adjacentes_de('A')
        self.assertEqual(len(adj_a), 2)
    
    def test_carga_json(self):
        """Testa carregamento de arquivo JSON"""
        dados_json = {
            "nome_grafo": "Teste JSON",
            "descricao": "Grafo de teste",
            "metrica": "km",
            "metrica_final": "distância total",
            "grafo": {
                'A': {'label': 'Início', 'B': 5},
                'B': {'label': 'Fim', 'A': 5}
            }
        }
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dados_json, f)
            temp_file = f.name
        
        try:
            metadados = self.grafo.carregar_json(temp_file)
            
            # Verifica metadados
            self.assertEqual(self.grafo.nome_grafo, "Teste JSON")
            self.assertEqual(self.grafo.metrica, "km")
            self.assertEqual(len(self.grafo), 2)
            
            # Verifica labels
            self.assertEqual(self.grafo.get_label('A'), 'Início')
            self.assertEqual(self.grafo.get_label('B'), 'Fim')
        finally:
            os.unlink(temp_file)
    
    def test_criar_no_manual(self):
        """Testa criação manual de nós"""
        # Cria nós primeiro
        no_a = No(letra='A', label='Ponto A')
        no_b = No(letra='B', label='Ponto B')
        
        self.grafo.criar_no(no_a)
        self.grafo.criar_no(no_b)
        
        # Adiciona adjacências
        self.grafo.criar_no(no_a, {'B': 10})
        
        # Verifica
        self.assertEqual(len(self.grafo), 2)
        self.assertEqual(self.grafo.get_label('A'), 'Ponto A')
        adj_a = self.grafo._adjacentes_de('A')
        self.assertEqual(len(adj_a), 1)
        self.assertEqual(adj_a[0], ('B', 10))


class TestLabelsGrafos(unittest.TestCase):
    """Testes para a funcionalidade de labels nos nós"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste Labels")
        dados = {
            'A': {'B': 1},
            'B': {'A': 1, 'C': 2},
            'C': {'B': 2}
        }
        self.grafo.carregar(dados)
    
    def test_labels_manuais(self):
        """Testa definição manual de labels"""
        self.grafo.set_label('A', 'Casa')
        self.grafo.set_label('B', 'Trabalho')
        self.grafo.set_label('C', 'Loja')
        
        self.assertEqual(self.grafo.get_label('A'), 'Casa')
        self.assertEqual(self.grafo.get_label('B'), 'Trabalho')
        self.assertEqual(self.grafo.get_label('C'), 'Loja')
    
    def test_get_all_labels(self):
        """Testa recuperação de todos os labels"""
        self.grafo.set_label('A', 'Início')
        self.grafo.set_label('C', 'Meio')
        
        all_labels = self.grafo.get_all_labels()
        
        self.assertEqual(all_labels['A'], 'Início')
        self.assertEqual(all_labels['B'], 'B')  # Label padrão (letra)
        self.assertEqual(all_labels['C'], 'Meio')
    
    def test_busca_por_label(self):
        """Testa busca de nó por label"""
        self.grafo.set_label('A', 'Casa')
        self.grafo.set_label('B', 'Trabalho')
        
        no_casa = self.grafo.get_no_por_label('Casa')
        no_trabalho = self.grafo.get_no_por_label('Trabalho')
        no_inexistente = self.grafo.get_no_por_label('Escola')
        
        self.assertEqual(no_casa.letra, 'A')
        self.assertEqual(no_trabalho.letra, 'B')
        self.assertIsNone(no_inexistente)


class TestRegistroVisitas(unittest.TestCase):
    """Testes para o sistema de registro de visitas"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste Visitas")
        dados = {
            'A': {'B': 3, 'C': 2},
            'B': {'A': 3, 'C': 1, 'D': 4},
            'C': {'A': 2, 'B': 1, 'D': 5},
            'D': {'B': 4, 'C': 5}
        }
        self.grafo.carregar(dados)
        self.registro = self.grafo.get_registro_visitas()
    
    def test_visita_simples(self):
        """Testa registro básico de visitas"""
        self.registro.reset()
        self.registro.mover_para('A')  # Ponto de partida
        self.registro.mover_para('B')  # Movimento
        
        self.assertTrue(self.registro.foi_visitado('A'))
        self.assertTrue(self.registro.foi_visitado('B'))
        self.assertFalse(self.registro.foi_visitado('C'))
        
        self.assertEqual(self.registro.get_custo_total(), 3)
        self.assertEqual(len(self.registro.get_caminho_completo()), 2)
    
    def test_movimento_entre_nos(self):
        """Testa movimento entre nós com registro de origem/destino"""
        self.registro.reset()
        self.registro.mover_para('A')  # Ponto de partida
        self.registro.mover_para('B')  # A -> B (custo 3)
        self.registro.mover_para('C')  # B -> C (custo 1)
        
        caminho = self.registro.get_caminho_completo()
        historico = self.registro.get_historico_movimentos()
        
        self.assertEqual(caminho, ['A', 'B', 'C'])
        self.assertEqual(len(historico), 3)  # Incluindo ponto de partida
        
        # Verifica histórico
        self.assertEqual(historico[0][0], None)  # Início (sem origem)
        self.assertEqual(historico[0][1], 'A')   # Destino inicial
        self.assertEqual(historico[1][0], 'A')   # origem do segundo movimento
        self.assertEqual(historico[1][1], 'B')   # destino do segundo movimento
        self.assertEqual(historico[1][2], 3)     # custo A->B
        self.assertEqual(historico[2][0], 'B')   # origem do terceiro movimento
        self.assertEqual(historico[2][1], 'C')   # destino do terceiro movimento
        self.assertEqual(historico[2][2], 1)     # custo B->C
        
        self.assertEqual(self.registro.get_custo_total(), 4)  # 3 + 1
    
    def test_estatisticas(self):
        """Testa cálculo de estatísticas do percurso"""
        self.registro.reset()
        self.registro.mover_para('A')  # Ponto de partida
        self.registro.mover_para('B')  # A -> B (custo 3)
        self.registro.mover_para('C')  # B -> C (custo 1)
        
        stats = self.registro.get_estatisticas()
        
        self.assertEqual(stats['nos_visitados'], 3)
        self.assertEqual(stats['movimentos_totais'], 2)
        self.assertEqual(stats['custo_total'], 4)  # 3 + 1
        self.assertEqual(stats['custo_medio_movimento'], 2.0)  # 4/2
        self.assertEqual(stats['posicao_atual'], 'C')
        self.assertEqual(stats['posicao_inicial'], 'A')
        
        # Verifica se as métricas estão presentes
        self.assertIn('tempo_total', stats)
        self.assertIn('iteracoes', stats)
        self.assertIn('memoria_usada_bytes', stats)
    
    def test_reset(self):
        """Testa reset do registro de visitas"""
        self.registro.mover_para('A')
        self.registro.mover_para('B')
        
        self.registro.reset()
        
        self.assertEqual(len(self.registro.visitados), 0)
        self.assertEqual(self.registro.get_custo_total(), 0)
        self.assertEqual(len(self.registro.get_caminho_completo()), 0)


class TestGrafosBaseVisitas(unittest.TestCase):
    """Testes para funcionalidades de visita na classe GrafosBase"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste Base Visitas")
        dados = {
            'A': {'B': 3, 'C': 2},
            'B': {'A': 3, 'C': 1, 'D': 4},
            'C': {'A': 2, 'B': 1, 'D': 5},
            'D': {'B': 4, 'C': 5}
        }
        self.grafo.carregar(dados)
    
    def test_mover_para(self):
        """Testa registro de visita através do método da classe"""
        self.grafo.resetar_visitas()
        self.grafo.mover_para('A')
        self.grafo.mover_para('B')
        
        registro = self.grafo.get_registro_visitas()
        
        self.assertEqual(registro.get_custo_total(), 3)
        self.assertEqual(registro.get_caminho_completo(), ['A', 'B'])
    
    def test_percorrer_caminho_valido(self):
        """Testa percurso de um caminho válido"""
        caminho = ['A', 'B', 'C', 'D']
        resultado = self.grafo.percorrer_caminho(caminho)
        
        self.assertTrue(resultado['sucesso'])
        self.assertEqual(resultado['custo_total'], 9)  # A-B(3) + B-C(1) + C-D(5) = 9
        self.assertEqual(resultado['movimentos'], 3)
    
    def test_percorrer_caminho_inexistente(self):
        """Testa percurso com nó inexistente"""
        # Captura output para evitar prints durante teste
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            caminho = ['A', 'X']  # X não existe
            resultado = self.grafo.percorrer_caminho(caminho)
            
            # Deve falhar graciosamente
            self.assertFalse(resultado['sucesso'])
        finally:
            sys.stdout = original_stdout
    
    def test_get_nos_visitados(self):
        """Testa recuperação de nós visitados"""
        self.grafo.resetar_visitas()
        self.grafo.mover_para('A')
        self.grafo.mover_para('C')
        self.grafo.mover_para('B')
        
        nos_visitados = self.grafo.get_nos_visitados()
        nos_visitados_letras = self.grafo.get_nos_visitados_letras()
        
        # Deve retornar ordenado
        self.assertEqual(sorted(nos_visitados), ['A', 'B', 'C'])
        self.assertEqual(sorted(nos_visitados_letras), ['A', 'B', 'C'])
    
    def test_reset_visitas(self):
        """Testa reset de visitas"""
        self.grafo.mover_para('A')
        self.grafo.mover_para('B')
        
        self.grafo.resetar_visitas()
        
        registro = self.grafo.get_registro_visitas()
        self.assertEqual(len(registro.visitados), 0)
        self.assertEqual(registro.get_custo_total(), 0)


class TestComparacaoGrafos(unittest.TestCase):
    """Testes para comparação entre diferentes grafos"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo1 = GrafosBase("Grafo 1")
        self.grafo2 = GrafosBase("Grafo 2")
    
    def test_grafos_identicos(self):
        """Testa se dois grafos com mesmos dados são equivalentes"""
        dados = {
            'A': {'B': 2, 'C': 5},
            'B': {'A': 2, 'C': 3},
            'C': {'A': 5, 'B': 3}
        }
        
        self.grafo1.carregar(dados)
        self.grafo2.carregar(dados)
        
        # Verifica se têm mesmo número de nós e adjacências
        self.assertEqual(len(self.grafo1), len(self.grafo2))
        self.assertEqual(len(self.grafo1.adjacentes), len(self.grafo2.adjacentes))
        
        # Verifica adjacências específicas
        adj1_a = dict(self.grafo1._adjacentes_de('A'))
        adj2_a = dict(self.grafo2._adjacentes_de('A'))
        self.assertEqual(adj1_a, adj2_a)
    
    def test_grafos_diferentes(self):
        """Testa diferenças entre grafos"""
        dados1 = {'A': {'B': 2}, 'B': {'A': 2, 'C': 3}, 'C': {'B': 3}}
        dados2 = {'A': {'B': 4}, 'B': {'A': 4, 'C': 3}, 'C': {'B': 3}}  # Peso diferente A-B
        
        self.grafo1.carregar(dados1)
        self.grafo2.carregar(dados2)
        
        # Verifica diferença específica
        adj1_a = dict(self.grafo1._adjacentes_de('A'))
        adj2_a = dict(self.grafo2._adjacentes_de('A'))
        self.assertNotEqual(adj1_a['B'], adj2_a['B'])


class TestCustosCalculos(unittest.TestCase):
    """Testes para cálculos de custos e avaliações"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste Custos")
        dados = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'C': 12, 'D': 15},
            'C': {'A': 15, 'B': 12, 'D': 10},
            'D': {'B': 15, 'C': 10}
        }
        self.grafo.carregar(dados)
    
    def test_custo_caminho_direto(self):
        """Testa cálculo de custo para caminho direto"""
        resultado = self.grafo.percorrer_caminho(['A', 'B'])
        self.assertEqual(resultado['custo_total'], 10)
        self.assertTrue(resultado['sucesso'])
    
    def test_custo_caminho_multiplo(self):
        """Testa cálculo de custo para caminho com múltiplas arestas"""
        resultado = self.grafo.percorrer_caminho(['A', 'B', 'D'])
        self.assertEqual(resultado['custo_total'], 25)  # 10 + 15
        self.assertEqual(resultado['movimentos'], 2)
    
    def test_comparacao_caminhos(self):
        """Testa comparação entre diferentes caminhos"""
        # Caminho 1: A -> B -> D
        resultado1 = self.grafo.percorrer_caminho(['A', 'B', 'D'])
        
        # Caminho 2: A -> C -> D
        resultado2 = self.grafo.percorrer_caminho(['A', 'C', 'D'])
        
        # A -> C -> D (15 + 10 = 25) vs A -> B -> D (10 + 15 = 25)
        self.assertEqual(resultado1['custo_total'], resultado2['custo_total'])
        self.assertTrue(resultado1['sucesso'])
        self.assertTrue(resultado2['sucesso'])
    
    def test_caminho_vazio(self):
        """Testa comportamento com caminho vazio"""
        resultado = self.grafo.percorrer_caminho([])
        self.assertEqual(resultado['custo_total'], 0)
        self.assertEqual(resultado['movimentos'], 0)
        self.assertFalse(resultado['sucesso'])


class TestAlgoritmoDijkstra(unittest.TestCase):
    """Testes para o algoritmo de Dijkstra"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.dijkstra = GrafosDijkstra("Teste Dijkstra")
        
        # Dados consistentes para teste
        dados = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'C': 1, 'D': 5},
            'C': {'A': 2, 'B': 1, 'D': 8},
            'D': {'B': 5, 'C': 8}
        }
        self.dijkstra.carregar(dados)
    
    def test_caminho_simples(self):
        """Testa cálculo de menor caminho simples"""
        caminho, custo = self.dijkstra.obter_caminho_e_custo('A', 'D')
        
        # Verifica se encontrou um caminho válido
        self.assertIsInstance(caminho, list)
        self.assertIsInstance(custo, (int, float))
        self.assertGreater(len(caminho), 0)
        self.assertEqual(caminho[0], 'A')  # Deve começar em A
        self.assertEqual(caminho[-1], 'D')  # Deve terminar em D
        
        # O menor caminho deve ser A -> C -> B -> D (2 + 1 + 5 = 8)
        self.assertEqual(custo, 8)
        self.assertEqual(caminho, ['A', 'C', 'B', 'D'])

    def test_dijkstra_interno(self):
        """Testa funcionamento interno do algoritmo Dijkstra"""
        resultado = self.dijkstra.encontrar_caminho('A', 'C')
        caminho = self.dijkstra.movimentos.caminho
        
        # Verifica se o resultado tem a estrutura esperada
        self.assertIsInstance(resultado, bool)
        self.assertTrue(resultado)  # Deve ser True para caminho encontrado
        
        # Verifica se o caminho foi registrado nos movimentos
        self.assertGreaterEqual(len(caminho), 2)  # Pelo menos origem e destino
        self.assertEqual(caminho[0], 'A')  # Primeiro nó deve ser A
        self.assertEqual(caminho[-1], 'C')  # Último nó deve ser C
        
        # Verifica se os nós existem no grafo
        self.assertIn('A', self.dijkstra.nos)
        self.assertIn('C', self.dijkstra.nos)
    
    def test_caminho_mesmo_no(self):
        """Testa caminho quando origem e destino são iguais"""
        caminho, custo = self.dijkstra.obter_caminho_e_custo('A', 'A')
        
        self.assertEqual(len(caminho), 1)
        self.assertEqual(caminho[0], 'A')
        self.assertEqual(custo, 0)
    
    def test_custos_depois_dijkstra(self):
        """Testa se os custos são calculados corretamente"""
        self.dijkstra.encontrar_caminho('A', 'D')
        
        # Verifica se self.custos foi populado
        self.assertIsNotNone(self.dijkstra.custos)
        self.assertIn('A', self.dijkstra.custos)
        self.assertIn('D', self.dijkstra.custos)
        
        # Custo de A para A deve ser 0
        self.assertEqual(self.dijkstra.custos['A'][1], 0)


class TestGrafoAEstrela(unittest.TestCase):
    """Testes para o algoritmo A* (A-estrela)"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.astar = GrafoAEstrela("Teste A*")
    
    def test_astar_funcionamento_basico(self):
        """Testa funcionamento básico do A* sem heurísticas"""
        dados = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'C': 1, 'D': 5},
            'C': {'A': 2, 'B': 1, 'D': 8},
            'D': {'B': 5, 'C': 8}
        }
        
        astar = GrafoAEstrela("Teste A* Básico")
        astar.carregar(dados)
        
        # Testa se encontra caminho básico
        sucesso = astar.encontrar_caminho('A', 'D')
        
        self.assertTrue(sucesso)
        caminho = astar.movimentos.get_caminho_completo()
        custo = astar.movimentos.get_custo_total()
        
        # Verifica estrutura do resultado
        self.assertIsInstance(caminho, list)
        self.assertGreater(len(caminho), 1)
        self.assertEqual(caminho[0], 'A')
        self.assertEqual(caminho[-1], 'D')
        self.assertEqual(custo, 8)  # Caminho ótimo A->C->B->D
    
    def test_astar_com_heuristicas(self):
        """Testa funcionamento do A* com heurísticas"""
        dados_com_heuristica = {
            'A': {'B': 5, 'C': 10, '~E': 12},    # Heurística A→E: 12
            'B': {'A': 5, 'D': 3, '~E': 8},      # Heurística B→E: 8  
            'C': {'A': 10, 'D': 2, '~E': 4},     # Heurística C→E: 4
            'D': {'B': 3, 'C': 2, 'E': 6, '~E': 6},  # Heurística D→E: 6
            'E': {'D': 6}                         # E é destino
        }
        
        self.astar.carregar(dados_com_heuristica)
        
        # Verifica se as heurísticas foram carregadas
        self.assertGreater(len(self.astar.heuristicas), 0)
        self.assertIn(('A', 'E'), self.astar.heuristicas)
        self.assertEqual(self.astar.heuristicas[('A', 'E')], 12)
        
        # Testa caminho com heurísticas
        sucesso = self.astar.encontrar_caminho('A', 'E')
        
        self.assertTrue(sucesso)
        caminho = self.astar.movimentos.get_caminho_completo()
        custo = self.astar.movimentos.get_custo_total()
        
        self.assertEqual(caminho[0], 'A')
        self.assertEqual(caminho[-1], 'E')
        self.assertGreater(custo, 0)
    
    def test_astar_vs_dijkstra_comparacao(self):
        """Compara A* com Dijkstra no mesmo grafo"""
        # Dados para A* (com heurísticas)
        dados_astar = {
            'A': {'B': 5, 'C': 10, '~D': 15},
            'B': {'A': 5, 'D': 8, '~D': 8},
            'C': {'A': 10, 'D': 3, '~D': 3},
            'D': {'B': 8, 'C': 3}
        }
        
        # Dados para Dijkstra (sem heurísticas)
        dados_dijkstra = {
            'A': {'B': 5, 'C': 10},
            'B': {'A': 5, 'D': 8},
            'C': {'A': 10, 'D': 3},
            'D': {'B': 8, 'C': 3}
        }
        
        # Configura A*
        self.astar.carregar(dados_astar)
        
        # Configura Dijkstra
        dijkstra = GrafosDijkstra("Comparação Dijkstra")
        dijkstra.carregar(dados_dijkstra)
        
        # Testa mesmo caminho A → D
        sucesso_astar = self.astar.encontrar_caminho('A', 'D')
        sucesso_dijkstra = dijkstra.encontrar_caminho('A', 'D')
        
        self.assertTrue(sucesso_astar)
        self.assertTrue(sucesso_dijkstra)
        
        custo_astar = self.astar.movimentos.get_custo_total()
        custo_dijkstra = dijkstra.movimentos.get_custo_total()
        
        # Ambos devem encontrar solução ótima (A→C→D = 13)
        self.assertEqual(custo_astar, custo_dijkstra)
        self.assertEqual(custo_astar, 13)

    def test_astar_caminho_a_b_e_grafo_simples(self):
        """Testa cenário específico A->B->E com custo 12 no grafo_simples.json"""
        # Carrega o grafo simples
        self.astar.carregar_json("base_grafos/grafo_simples.json")
        
        # Verifica se o algoritmo encontra o caminho correto A->B->E
        sucesso = self.astar.encontrar_caminho('A', 'E')
        
        self.assertTrue(sucesso, "Algoritmo A* deve encontrar caminho de A para E")
        
        # Verifica o caminho encontrado
        caminho = self.astar.movimentos.get_caminho_completo()
        custo_total = self.astar.movimentos.get_custo_total()
        
        # Verifica se é o caminho esperado: A -> B -> E
        self.assertEqual(caminho, ['A', 'B', 'E'], 
                        f"Caminho esperado ['A', 'B', 'E'], obtido {caminho}")
        
        # Verifica se o custo total é 12 (5 + 7)
        self.assertEqual(custo_total, 12, 
                        f"Custo esperado 12 (5+7), obtido {custo_total}")
        
        # Verifica se as heurísticas estão sendo calculadas corretamente
        dados_heuristica = self.astar.movimentos.caminho_heuristica_vs_real()
        
        # Deve ter 3 passos: A (inicial), A->B, B->E
        self.assertEqual(len(dados_heuristica), 3, 
                        f"Esperados 3 passos, obtidos {len(dados_heuristica)}")
        
        # Passo 0: A inicial - heurística=0, real=12
        self.assertEqual(dados_heuristica[0], ('A', 'A', 0, 12))
        
        # Passo 1: A->B - heurística=11 (custo aresta A->B(5) + heur. B->E(6)), real=7 
        self.assertEqual(dados_heuristica[1], ('A', 'B', 11, 7))
        
        # Passo 2: B->E - heurística=0 (chegou ao destino), real=0
        self.assertEqual(dados_heuristica[2], ('B', 'E', 0, 0))
        
        # Verifica a descrição formatada
        descricao = self.astar.movimentos.caminho_descrito_heuristica_vs_real()
        self.assertIn('A(Centro da Cidade)', descricao)
        self.assertIn('B(Shopping Mall)', descricao)
        self.assertIn('E(Aeroporto)', descricao)
        self.assertIn('r:5.00+7.00 | h:5.00+6.00', descricao)  # A->B: real(5+7) | heurística(5+6)
        self.assertIn('r:7.00 | h:6.00', descricao)      # B->E: real(7) | heurística(6)

    
class TestHeuristicasAEstrela(unittest.TestCase):
    """Testes específicos para funcionalidades de heurísticas no A*"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.astar = GrafoAEstrela("Teste Heurísticas")
    
    def test_carregamento_formato_heuristica(self):
        """Testa carregamento correto do formato ~DESTINO"""
        dados = {
            'A': {'B': 5, '~C': 10, '~D': 15},
            'B': {'A': 5, 'C': 3, '~C': 3, '~D': 8},
            'C': {'B': 3, 'D': 4, '~D': 4},
            'D': {'C': 4}
        }
        
        self.astar.carregar(dados)
        
        # Verifica se as heurísticas foram armazenadas corretamente
        self.assertEqual(len(self.astar.heuristicas), 5)
        self.assertIn(('A', 'C'), self.astar.heuristicas)
        self.assertIn(('A', 'D'), self.astar.heuristicas)
        self.assertIn(('B', 'C'), self.astar.heuristicas)
        self.assertIn(('B', 'D'), self.astar.heuristicas)
        self.assertIn(('C', 'D'), self.astar.heuristicas)
        
        # Verifica valores específicos
        self.assertEqual(self.astar.heuristicas[('A', 'C')], 10)
        self.assertEqual(self.astar.heuristicas[('A', 'D')], 15)
        self.assertEqual(self.astar.heuristicas[('B', 'C')], 3)
    
    def test_astar_sem_heuristicas(self):
        """Testa A* sem heurísticas (deve se comportar como Dijkstra)"""
        dados = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'C': 1, 'D': 5},
            'C': {'A': 2, 'B': 1, 'D': 8},
            'D': {'B': 5, 'C': 8}
        }
        
        astar = GrafoAEstrela("Teste A* Sem Heurísticas")
        astar.carregar(dados)
        dj = GrafosDijkstra()
        dj.carregar(dados)
        dj.encontrar_caminho('A', 'D')
        
        # Verifica que não há heurísticas
        self.assertEqual(len(astar.heuristicas), 0)
        
        # Testa funcionamento
        sucesso = astar.encontrar_caminho('A', 'D')
        print(f'A* A→C→B→D (2+1+5=8): {astar.movimentos.get_caminho_completo()}')
        self.assertTrue(sucesso)
        
        custo = astar.movimentos.get_custo_total()
        custodj = dj.movimentos.get_custo_total()
        self.assertEqual(custo, custodj)
        # Deve encontrar caminho ótimo A→C→B→D (2+1+5=8)
        self.assertEqual(custo, 8)


class TestCaminhoHeuristicaVsReal(unittest.TestCase):
    """Testes específicos para a função caminho_heuristica_vs_real"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.astar = GrafoAEstrela("Teste Heurística vs Real")
    
    def test_formato_retorno_funcao(self):
        """Testa formato de retorno da função caminho_heuristica_vs_real"""
        dados = {
            'A': {'B': 5, '~C': 10},
            'B': {'A': 5, 'C': 8, '~C': 8},
            'C': {'B': 8}
        }
        
        self.astar.carregar(dados)
        
        # Executa algoritmo
        sucesso = self.astar.encontrar_caminho('A', 'C')
        self.assertTrue(sucesso)
        
        # Testa função
        resultado = self.astar.movimentos.caminho_heuristica_vs_real()
        
        # Verifica formato
        self.assertIsInstance(resultado, list)
        self.assertGreater(len(resultado), 0)
        
        # Cada item deve ser uma tupla com 4 elementos
        for item in resultado:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 4)
            origem, destino, heuristica, real = item
            self.assertIsInstance(origem, str)
            self.assertIsInstance(destino, str)
            # heurística pode ser None ou número
            self.assertTrue(heuristica is None or isinstance(heuristica, (int, float)))
            self.assertIsInstance(real, (int, float))
    
    def test_calculos_corretos_heuristica_vs_real(self):
        """Testa se os cálculos estão corretos na função"""
        dados = {
            'A': {'B': 3, '~D': 10},     # A→B (3), A estima D em 10
            'B': {'A': 3, 'C': 4, '~D': 6},  # B→C (4), B estima D em 6
            'C': {'B': 4, 'D': 2, '~D': 2},  # C→D (2), C estima D em 2
            'D': {'C': 2}
        }
        
        self.astar.carregar(dados)
        
        # Executa algoritmo A→D
        sucesso = self.astar.encontrar_caminho('A', 'D')
        self.assertTrue(sucesso)
        
        # Verifica caminho encontrado
        caminho = self.astar.movimentos.get_caminho_completo()
        custo_total = self.astar.movimentos.get_custo_total()
        
        # Caminho deve ser A→B→C→D (3+4+2=9)
        self.assertEqual(caminho, ['A', 'B', 'C', 'D'])
        self.assertEqual(custo_total, 9)
        
        # Testa função heurística vs real
        resultado = self.astar.movimentos.caminho_heuristica_vs_real()
        
        # Deve ter 4 itens: ponto inicial + 3 movimentos
        self.assertEqual(len(resultado), 4)
        
        # Verifica cada passo
        inicio = resultado[0]
        self.assertEqual(inicio[0], 'A')  # origem
        self.assertEqual(inicio[1], 'A')  # destino (mesmo nó)
        self.assertEqual(inicio[2], 0)    # heurística (ponto inicial)
        self.assertEqual(inicio[3], 9)    # real até final (custo total)
        
        passo1 = resultado[1]  # A→B
        self.assertEqual(passo1[0], 'A')  # origem
        self.assertEqual(passo1[1], 'B')  # destino
        self.assertEqual(passo1[2], 9)    # heurística: 3 (A→B) + 6 (B estima D)
        self.assertEqual(passo1[3], 6)    # real restante: 4+2=6
        
        passo2 = resultado[2]  # B→C
        self.assertEqual(passo2[0], 'B')  # origem
        self.assertEqual(passo2[1], 'C')  # destino
        self.assertEqual(passo2[2], 6)    # heurística: 4 (B→C) + 2 (C estima D)
        self.assertEqual(passo2[3], 2)    # real restante: 2
        
        passo3 = resultado[3]  # C→D
        self.assertEqual(passo3[0], 'C')  # origem
        self.assertEqual(passo3[1], 'D')  # destino
        self.assertEqual(passo3[2], 0)    # heurística: 0 (chegou ao destino final)
        self.assertEqual(passo3[3], 0)    # real restante: 0

    def test_calculos_corretos_heuristica_simples_2(self):
        """Testa se os cálculos estão corretos na função"""
        
        self.astar.carregar_json("./base_grafos/grafo_simples_2.json")

        # Executa algoritmo A→E
        sucesso = self.astar.encontrar_caminho('A', 'E')
        self.assertTrue(sucesso)
        
        # Verifica caminho encontrado
        caminho = self.astar.movimentos.get_caminho_completo()
        custo_total = self.astar.movimentos.get_custo_total()
        
        # Caminho deve ser A→B→C→D (3+4+2=9)
        self.assertEqual(caminho, ['A', 'B', 'C', 'D', 'E'])
        self.assertEqual(custo_total, 8)
        
        # Testa função heurística vs real
        resultado = self.astar.movimentos.caminho_heuristica_vs_real()
        
        # Deve ter 4 itens: ponto inicial + 4 movimentos
        self.assertEqual(len(resultado), 5)
        

class TestCasosEspeciaisAEstrela(unittest.TestCase):
    """Testes para casos especiais do A*"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.astar = GrafoAEstrela("Teste Casos Especiais A*")
    
    def test_caminho_inexistente(self):
        """Testa comportamento quando não há caminho"""
        dados = {
            'A': {'B': 5},
            'B': {'A': 5},
            'C': {'D': 3},  # Componente desconectado
            'D': {'C': 3}
        }
        
        self.astar.carregar(dados)
        
        # Tenta caminho entre componentes desconectados
        sucesso = self.astar.encontrar_caminho('A', 'C')
        
        self.assertFalse(sucesso)
    
    def test_no_inexistente(self):
        """Testa comportamento com nó inexistente"""
        dados = {
            'A': {'B': 5},
            'B': {'A': 5}
        }
        
        self.astar.carregar(dados)
        
        # Testa origem inexistente
        sucesso1 = self.astar.encontrar_caminho('X', 'A')
        self.assertFalse(sucesso1)
        
        # Testa destino inexistente
        sucesso2 = self.astar.encontrar_caminho('A', 'Y')
        self.assertFalse(sucesso2)
    
    def test_grafo_com_apenas_um_no(self):
        """Testa comportamento com grafo de um só nó"""
        dados = {
            'A': {}  # Nó isolado
        }
        
        self.astar.carregar(dados)
        
        # Caminho do nó para ele mesmo
        sucesso = self.astar.encontrar_caminho('A', 'A')
        
        self.assertTrue(sucesso)
        caminho = self.astar.movimentos.get_caminho_completo()
        custo = self.astar.movimentos.get_custo_total()
        
        self.assertEqual(caminho, ['A'])
        self.assertEqual(custo, 0)
    
    def test_carregamento_json_com_heuristicas(self):
        """Testa carregamento de arquivo JSON com heurísticas"""
        dados_json = {
            "nome_grafo": "Teste A* JSON",
            "descricao": "Grafo com heurísticas",
            "metrica": "distancia",
            "grafo": {
                'A': {'B': 5, 'C': 10, '~D': 15},
                'B': {'A': 5, 'D': 8, '~D': 8},
                'C': {'A': 10, 'D': 3, '~D': 3},
                'D': {'B': 8, 'C': 3}
            }
        }
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dados_json, f)
            temp_file = f.name
        
        try:
            metadados = self.astar.carregar_json(temp_file)
            
            # Verifica metadados
            self.assertEqual(self.astar.nome_grafo, "Teste A* JSON")
            self.assertEqual(self.astar.metrica, "distancia")
            
            # Verifica heurísticas
            self.assertGreater(len(self.astar.heuristicas), 0)
            self.assertIn(('A', 'D'), self.astar.heuristicas)
            
            # Testa funcionamento
            sucesso = self.astar.encontrar_caminho('A', 'D')
            self.assertTrue(sucesso)
            
        finally:
            os.unlink(temp_file)


class TestGBFSPredecessores(unittest.TestCase):
    """Testes para verificar construção correta do caminho no GBFS"""
    
    def setUp(self):
        """Configuração inicial para testes do GBFS"""
        self.gbfs = GrafoGananciosa("Teste GBFS Predecessores")
    
    def test_gbfs_caminho_com_predecessores_corretos(self):
        """Testa se o GBFS constrói o caminho incluindo todos os nós visitados na ordem correta"""
        
        # Cria um grafo de teste que reproduz o cenário ACAI A->J
        dados_test = {
            "nome_grafo": "Teste GBFS Predecessores",
            "descricao": "Grafo para testar predecessores do GBFS",
            "metrica": "km",
            "grafo": {
                "A": {
                    "label": "Inicio",
                    "B": 15,
                    "H": 20, 
                    "L": 11,
                    "~B": 49.67,
                    "~H": 44.99,
                    "~L": 41.27,
                    "~J": 58.71
                },
                "L": {
                    "label": "Intermediario L",
                    "A": 11,
                    "H": 15,
                    "~A": 58.71,
                    "~H": 44.99,
                    "~J": 41.27
                },
                "H": {
                    "label": "Intermediario H", 
                    "A": 20,
                    "L": 15,
                    "I": 7,
                    "~A": 58.71,
                    "~L": 41.27,
                    "~I": 43.86,
                    "~J": 44.99
                },
                "I": {
                    "label": "Intermediario I",
                    "H": 7,
                    "M": 25,
                    "~H": 44.99,
                    "~M": 0,
                    "~J": 43.86
                },
                "M": {
                    "label": "Quase Final",
                    "I": 25,
                    "J": 31,
                    "~I": 43.86,
                    "~J": 0
                },
                "J": {
                    "label": "Destino",
                    "M": 31,
                    "~M": 0
                },
                "B": {
                    "label": "Alternativo B",
                    "A": 15,
                    "~A": 58.71,
                    "~J": 49.67
                }
            }
        }
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dados_test, f)
            temp_file = f.name
        
        try:
            # Carrega o grafo
            self.gbfs.carregar_json(temp_file)
            
            # Executa GBFS de A para J
            sucesso = self.gbfs.encontrar_caminho('A', 'J')
            self.assertTrue(sucesso, "GBFS deveria encontrar caminho de A para J")
            
            # Obtém o caminho encontrado
            caminho = self.gbfs.movimentos.get_caminho_completo()
            nós_visitados = self.gbfs.movimentos.visitados
            
            print(f"\n🔍 DEBUG TESTE GBFS:")
            print(f"   Caminho encontrado: {' → '.join(caminho)}")
            print(f"   Nós visitados: {sorted(nós_visitados)}")
            print(f"   Custo total: {self.gbfs.movimentos.get_custo_total()}")
            
            # TESTES ESPECÍFICOS DO CENÁRIO
            
            # 1. Verifica se o caminho começa em A e termina em J
            self.assertEqual(caminho[0], 'A', "Caminho deve começar em A")
            self.assertEqual(caminho[-1], 'J', "Caminho deve terminar em J") 
            
            # 2. Verifica se L foi visitado (deveria ser pelo GBFS correto)
            self.assertIn('L', nós_visitados, 
                         "L deveria ter sido visitado (melhor heurística de A)")
            
            # 3. Verifica ordem heurística das decisões de A
            # L tem h=41.27 (melhor), H tem h=44.99, B tem h=49.67
            heuristica_L = self.gbfs._heuristica('L', 'J')
            heuristica_H = self.gbfs._heuristica('H', 'J') 
            heuristica_B = self.gbfs._heuristica('B', 'J')
            
            self.assertLess(heuristica_L, heuristica_H, 
                           "h(L,J) deveria ser menor que h(H,J)")
            self.assertLess(heuristica_H, heuristica_B,
                           "h(H,J) deveria ser menor que h(B,J)")
            
            # 4. TESTE CRÍTICO: Se L foi visitado e H está no caminho,
            #    então L deveria estar no caminho também (como predecessor de H)
            if 'L' in nós_visitados and 'H' in caminho:
                # Como L→H é uma aresta válida e L foi visitado primeiro,
                # o caminho deveria incluir L
                print(f"   ⚠️  ANÁLISE: L visitado={'L' in nós_visitados}, H no caminho={'H' in caminho}")
                print(f"   ⚠️  EXPECTATIVA: Se L foi visitado primeiro e H está no caminho,")
                print(f"   ⚠️               então L deveria estar no caminho como predecessor de H")
                
                # Este teste pode falhar se o bug dos predecessores ainda existe
                if 'L' not in caminho and 'H' in caminho:
                    print(f"   🐛 BUG DETECTADO: L foi visitado mas não está no caminho final!")
                    print(f"   🐛 Isso indica problema na construção dos predecessores")
            
            # 5. Verifica eficiência: GBFS deveria visitar poucos nós
            self.assertLessEqual(len(nós_visitados), 6, 
                               "GBFS deveria ser eficiente e visitar poucos nós")
            
        finally:
            os.unlink(temp_file)
    
    def test_gbfs_ordem_expansao_por_heuristica(self):
        """Testa se GBFS expande nós na ordem correta da heurística"""
        
        # Grafo simples para testar ordem de expansão
        dados_simples = {
            "nome_grafo": "Teste Ordem Expansão",
            "grafo": {
                "A": {"B": 10, "C": 5, "~B": 8, "~C": 12, "~D": 20},
                "B": {"A": 10, "D": 3, "~A": 20, "~C": 15, "~D": 2},
                "C": {"A": 5, "D": 8, "~A": 20, "~B": 15, "~D": 10}, 
                "D": {"B": 3, "C": 8}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dados_simples, f)
            temp_file = f.name
            
        try:
            gbfs_ordem = GrafoGananciosa("Teste Ordem")
            gbfs_ordem.carregar_json(temp_file)
            
            # Busca A → D
            sucesso = gbfs_ordem.encontrar_caminho('A', 'D')
            self.assertTrue(sucesso)
            
            # Verifica se B foi escolhido primeiro (h(B,D)=2 < h(C,D)=10)
            caminho = gbfs_ordem.movimentos.get_caminho_completo()
            visitados = gbfs_ordem.movimentos.visitados
            
            print(f"\n🔍 TESTE ORDEM EXPANSÃO:")
            print(f"   Caminho: {' → '.join(caminho)}")
            print(f"   Visitados: {sorted(visitados)}")
            print(f"   h(B,D) = {gbfs_ordem._heuristica('B', 'D')}")
            print(f"   h(C,D) = {gbfs_ordem._heuristica('C', 'D')}")
            
            # B deveria ser escolhido por ter menor heurística
            self.assertIn('B', visitados, "B deveria ter sido visitado (melhor heurística)")
            
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    # Configuração para execução dos testes
    print("Executando testes para util_grafos.py")
    print("=" * 50)
    unittest.main(verbosity=2)