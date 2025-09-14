#!/usr/bin/env python3
"""
Teste específico para validar a implementação da estrutura ArrayLinkedList.
"""
# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_estrutura import ArrayLinkedList

def test_basic_functionality():
    """Testa funcionalidade básica da estrutura."""
    print("=== Teste de Funcionalidade Básica ===")
    
    # Teste com inserção no início (default_pos=0)
    ds = ArrayLinkedList(default_pos=0)
    
    # Teste de inserção
    result1 = ds.insert("000001", {"nome": "João", "idade": 25})
    result2 = ds.insert("000002", {"nome": "Maria", "idade": 30})
    result3 = ds.insert("000001", {"nome": "Pedro", "idade": 35})  # duplicata
    
    print(f"Inserção 1: {result1} (esperado: True)")
    print(f"Inserção 2: {result2} (esperado: True)")
    print(f"Inserção duplicata: {result3} (esperado: False)")
    
    # Teste de busca
    found1 = ds.search("000001")
    found2 = ds.search("000002")
    found3 = ds.search("000003")  # não existe
    
    print(f"Busca 000001: {found1 is not None} (esperado: True)")
    print(f"Busca 000002: {found2 is not None} (esperado: True)")
    print(f"Busca 000003: {found3 is not None} (esperado: False)")
    
    # Teste de remoção
    removed1 = ds.remove("000001")
    removed2 = ds.remove("000003")  # não existe
    
    print(f"Remoção 000001: {removed1} (esperado: True)")
    print(f"Remoção 000003: {removed2} (esperado: False)")
    
    print(f"Tamanho final: {ds.length} (esperado: 1)")
    print()

def test_metrics_counting():
    """Testa se as métricas estão sendo contadas corretamente."""
    print("=== Teste de Contagem de Métricas ===")
    
    # Teste com inserção no final (default_pos=-1)
    ds = ArrayLinkedList(default_pos=-1)
    
    # Limpa o log para contagem limpa
    ds.clear_log()
    
    # Insere 3 elementos
    ds.insert("000001", {"nome": "João"})
    ds.insert("000002", {"nome": "Maria"})  
    ds.insert("000003", {"nome": "Pedro"})
    
    summary = ds.summary("sum")
    insert_metrics = summary.get("insert", {})
    
    print("Métricas de inserção:")
    print(f"  - Comparações: {insert_metrics.get('comparisons', 0)}")
    print(f"  - Shifts: {insert_metrics.get('shifts', 0)}")
    print(f"  - Visitas de nós: {insert_metrics.get('node_visits', 0)}")
    print(f"  - Mem moves: {insert_metrics.get('mem_moves', 0)}")
    
    # Análise esperada para inserção no final:
    # - 1º elemento: 2 shifts (head, tail), 0 comparações
    # - 2º elemento: 2 shifts (tail.next, tail), 1 comparação (verifica duplicata)
    # - 3º elemento: 2 shifts (tail.next, tail), 2 comparações (verifica duplicatas)
    # Total esperado: 6 shifts, 3 comparações, 3 visitas
    
    print(f"\nAnálise:")
    print(f"  Shifts esperados: 6, obtidos: {insert_metrics.get('shifts', 0)}")
    print(f"  Comparações esperadas: 3, obtidas: {insert_metrics.get('comparisons', 0)}")
    print()

def test_sorted_insertion():
    """Testa inserção ordenada."""
    print("=== Teste de Inserção Ordenada ===")
    
    ds = ArrayLinkedList(sorted_insert=True)
    ds.clear_log()
    
    # Insere em ordem não-sequencial para testar ordenação
    ds.insert("000003", {"nome": "Pedro"})
    ds.insert("000001", {"nome": "João"})
    ds.insert("000002", {"nome": "Maria"})
    
    # Verifica se estão ordenados
    items = ds.to_list()
    print("Items na lista (deveriam estar ordenados):")
    for key, value in items:
        print(f"  {key}: {value['nome']}")
    
    # Verifica métricas de inserção ordenada
    summary = ds.summary("sum")
    insert_metrics = summary.get("insert", {})
    
    print(f"\nMétricas de inserção ordenada:")
    print(f"  - Comparações: {insert_metrics.get('comparisons', 0)}")
    print(f"  - Shifts: {insert_metrics.get('shifts', 0)}")
    print(f"  - Visitas de nós: {insert_metrics.get('node_visits', 0)}")
    print()

def test_position_insertion():
    """Testa inserção em posições específicas."""
    print("=== Teste de Inserção por Posição ===")
    
    # Teste inserção no meio (posição 1)
    ds = ArrayLinkedList(default_pos=1)
    ds.clear_log()
    
    ds.insert("000001", {"nome": "João"})     # posição 0 (primeiro)
    ds.insert("000002", {"nome": "Maria"})    # posição 1 (meio)
    ds.insert("000003", {"nome": "Pedro"})    # posição 1 (meio, empurra Maria)
    
    items = ds.to_list()
    print("Items após inserção na posição 1:")
    for i, (key, value) in enumerate(items):
        print(f"  pos {i}: {key} - {value['nome']}")
    
    print()

if __name__ == "__main__":
    test_basic_functionality()
    test_metrics_counting()
    test_sorted_insertion()
    test_position_insertion()
    
    print("=== Teste com Dados Reais ===")
    # Teste rápido com dados reais
    ds = ArrayLinkedList(default_pos=-1)
    ds.carregar_dados(100)
    ds.print_summary('sum')
