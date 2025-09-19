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

from util_grafos import GrafosBase, GrafosDijkstra, RegistroVisitas, No


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
        self.assertIsNone(self.grafo.get_label('D'))  # Sem label
        
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
        
        dados = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'C': 1, 'D': 5},
            'C': {'A': 2, 'B': 1, 'D': 8},
            'D': {'B': 5, 'C': 8}
        }
        self.dijkstra.carregar(dados)
    
    def test_caminho_simples(self):
        """Testa cálculo de menor caminho simples"""
        caminho, custo = self.dijkstra.caminho('A', 'D')
        
        # Verifica se encontrou um caminho válido
        self.assertIsInstance(caminho, list)
        self.assertIsInstance(custo, (int, float))
        self.assertGreater(len(caminho), 0)
        self.assertEqual(caminho[0], 'A')  # Deve começar em A
        self.assertEqual(caminho[-1], 'D')  # Deve terminar em D
        
        # O menor caminho deve ser A -> C -> B -> D (2 + 1 + 5 = 8)
        # ou A -> B -> D (4 + 5 = 9)
        # O algoritmo deve escolher o menor
        self.assertLessEqual(custo, 9)
    
    def test_dijkstra_interno(self):
        """Testa funcionamento interno do algoritmo Dijkstra"""
        resultado = self.dijkstra.dijkstra('A', 'D')
        
        # Verifica se o resultado tem a estrutura esperada
        self.assertIsInstance(resultado, tuple)
        self.assertEqual(len(resultado), 3)  # (nó, custo, anterior)
        self.assertEqual(resultado[0], 'D')  # Nó de destino
        self.assertIsInstance(resultado[1], (int, float))  # Custo
    
    def test_caminho_mesmo_no(self):
        """Testa caminho quando origem e destino são iguais"""
        caminho, custo = self.dijkstra.caminho('A', 'A')
        
        self.assertEqual(len(caminho), 1)
        self.assertEqual(caminho[0], 'A')
        self.assertEqual(custo, 0)
    
    def test_custos_depois_dijkstra(self):
        """Testa se os custos são calculados corretamente"""
        self.dijkstra.dijkstra('A', 'D')
        
        # Verifica se self.custos foi populado
        self.assertIsNotNone(self.dijkstra.custos)
        self.assertIn('A', self.dijkstra.custos)
        self.assertIn('D', self.dijkstra.custos)
        
        # Custo de A para A deve ser 0
        self.assertEqual(self.dijkstra.custos['A'][1], 0)


class TestCasosEspeciais(unittest.TestCase):
    """Testes para casos especiais e edge cases"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.grafo = GrafosBase("Teste Casos Especiais")
    
    def test_grafo_vazio(self):
        """Testa comportamento com grafo vazio"""
        self.assertEqual(len(self.grafo), 0)
        self.assertEqual(len(self.grafo.adjacentes), 0)
    
    def test_no_isolado(self):
        """Testa comportamento com nó isolado"""
        dados = {
            'A': {},  # Nó sem adjacentes
            'B': {'C': 1},
            'C': {'B': 1}
        }
        
        self.grafo.carregar(dados)
        
        # Verifica que A existe mas não tem adjacentes
        self.assertIn('A', self.grafo.nos)
        adj_a = self.grafo._adjacentes_de('A')
        self.assertEqual(len(adj_a), 0)
        
        # B e C devem ter adjacentes
        adj_b = self.grafo._adjacentes_de('B')
        self.assertEqual(len(adj_b), 1)
    
    def test_valores_limite(self):
        """Testa valores nos limites"""
        dados = {
            'A': {'B': 0, 'C': 999999},  # Peso zero e muito alto
            'B': {'A': 0},
            'C': {'A': 999999}
        }
        
        self.grafo.carregar(dados)
        
        adj_a = dict(self.grafo._adjacentes_de('A'))
        self.assertEqual(adj_a['B'], 0)
        self.assertEqual(adj_a['C'], 999999)
    
    def test_string_representacao(self):
        """Testa representação string do registro de visitas"""
        dados = {'A': {'B': 5}, 'B': {'A': 5}}
        self.grafo.carregar(dados)
        
        self.grafo.set_label('A', 'Início')
        self.grafo.set_label('B', 'Fim')
        
        self.grafo.mover_para('A')
        self.grafo.mover_para('B')
        
        registro = self.grafo.get_registro_visitas()
        string_repr = str(registro)
        
        self.assertIn('A(Início)', string_repr)
        self.assertIn('B(Fim)', string_repr)
        self.assertIn('Custo Total: 5', string_repr)


if __name__ == '__main__':
    # Configuração para execução dos testes
    print("Executando testes para util_grafos.py")
    print("=" * 50)
    unittest.main(verbosity=2)