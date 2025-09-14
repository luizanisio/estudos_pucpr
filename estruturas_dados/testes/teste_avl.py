#!/usr/bin/env python3
"""
Teste específico para validar a implementação da estrutura AVLTreeDS.
"""
# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_estrutura import AVLTreeDS

def test_avl_basic_functionality():
    """Testa funcionalidade básica da AVL Tree."""
    print("=== Teste de Funcionalidade Básica AVL ===")
    
    avl = AVLTreeDS()
    
    # Teste de inserção
    result1 = avl.insert("000003", {"nome": "Carlos", "idade": 30})
    result2 = avl.insert("000001", {"nome": "Ana", "idade": 25})
    result3 = avl.insert("000005", {"nome": "Eduardo", "idade": 35})
    result4 = avl.insert("000002", {"nome": "Bruno", "idade": 28})
    result5 = avl.insert("000004", {"nome": "Diana", "idade": 32})
    result6 = avl.insert("000003", {"nome": "Carlos2", "idade": 31})  # duplicata
    
    print(f"Inserção 000003: {result1} (esperado: True)")
    print(f"Inserção 000001: {result2} (esperado: True)")
    print(f"Inserção 000005: {result3} (esperado: True)")
    print(f"Inserção 000002: {result4} (esperado: True)")
    print(f"Inserção 000004: {result5} (esperado: True)")
    print(f"Inserção duplicata: {result6} (esperado: False)")
    
    # Teste de busca
    found1 = avl.search("000001")
    found2 = avl.search("000003")
    found3 = avl.search("000006")  # não existe
    
    print(f"Busca 000001: {found1 is not None} (esperado: True)")
    print(f"Busca 000003: {found2 is not None} (esperado: True)")
    print(f"Busca 000006: {found3 is not None} (esperado: False)")
    
    # Teste de remoção
    removed1 = avl.remove("000003")  # nó com 2 filhos
    removed2 = avl.remove("000006")  # não existe
    removed3 = avl.remove("000005")  # nó folha
    
    print(f"Remoção 000003: {removed1} (esperado: True)")
    print(f"Remoção 000006: {removed2} (esperado: False)")
    print(f"Remoção 000005: {removed3} (esperado: True)")
    
    # Verificar ordem após inserções/remoções
    print("Items em ordem:")
    for key, value in avl.inorder_items():
        print(f"  {key}: {value['nome']}")
    print()

def test_avl_balance_and_rotations():
    """Testa balanceamento e rotações da AVL."""
    print("=== Teste de Balanceamento AVL ===")
    
    avl = AVLTreeDS()
    avl.clear_log()
    
    # Inserção que deve causar rotações
    # Caso RR (Right-Right): inserir em ordem crescente
    print("Inserindo sequência que causa rotação RR...")
    avl.insert("000001", {"nome": "A"})
    avl.insert("000002", {"nome": "B"})
    avl.insert("000003", {"nome": "C"})  # deve causar rotação
    
    # Caso LL (Left-Left): forçar desbalanceamento à esquerda
    print("Inserindo sequência que causa rotação LL...")
    avl.insert("000000", {"nome": "Z"})  # deve causar rotação
    
    # Caso LR e RL: inserções que causam rotações duplas
    print("Inserindo sequência que causa rotações LR/RL...")
    avl.insert("000004", {"nome": "D"})
    avl.insert("000005", {"nome": "E"})
    avl.insert("000004.5", {"nome": "D5"})  # pode causar rotação dupla
    
    summary = avl.summary("sum")
    insert_metrics = summary.get("insert", {})
    
    print(f"\nMétricas de inserção com rotações:")
    print(f"  - Comparações: {insert_metrics.get('comparisons', 0)}")
    print(f"  - Rotações: {insert_metrics.get('rotations', 0)} (esperado: > 0)")
    print(f"  - Visitas de nós: {insert_metrics.get('node_visits', 0)}")
    print(f"  - Shifts: {insert_metrics.get('shifts', 0)}")
    
    print("Items finais em ordem (deve estar balanceado):")
    for key, value in avl.inorder_items():
        print(f"  {key}: {value['nome']}")
    print()

def test_avl_search_performance():
    """Testa performance de busca na AVL."""
    print("=== Teste de Performance de Busca AVL ===")
    
    avl = AVLTreeDS()
    
    # Insere 15 elementos para ter uma árvore razoável
    keys = ["000008", "000004", "000012", "000002", "000006", "000010", "000014",
            "000001", "000003", "000005", "000007", "000009", "000011", "000013", "000015"]
    
    for key in keys:
        avl.insert(key, {"nome": f"Nome{key}", "valor": int(key)})
    
    avl.clear_log()
    
    # Busca em diferentes posições da árvore
    # Raiz (deve ser rápida)
    result1 = avl.search("000008")
    # Nó folha (deve ser mais lenta)
    result2 = avl.search("000001")
    result3 = avl.search("000015")
    # Não existe (deve percorrer até folha)
    result4 = avl.search("000020")
    
    summary = avl.summary("sum")
    search_metrics = summary.get("search", {})
    
    print(f"Métricas de busca (4 buscas):")
    print(f"  - Comparações: {search_metrics.get('comparisons', 0)}")
    print(f"  - Visitas de nós: {search_metrics.get('node_visits', 0)}")
    print(f"  - Comparações por busca (média): {search_metrics.get('comparisons', 0) / 4:.1f}")
    print(f"  - Visitas por busca (média): {search_metrics.get('node_visits', 0) / 4:.1f}")
    
    # Para uma AVL bem balanceada com 15 nós, a altura máxima deve ser ~4
    # Logo, busca deve ser O(log n) ≈ 4 comparações máximo
    print(f"  - Performance esperada: O(log 15) ≈ 4 comparações por busca")
    print()

def test_avl_removal_cases():
    """Testa diferentes casos de remoção na AVL."""
    print("=== Teste de Casos de Remoção AVL ===")
    
    avl = AVLTreeDS()
    
    # Constrói árvore com estrutura conhecida
    keys = ["000005", "000003", "000007", "000002", "000004", "000006", "000008"]
    for key in keys:
        avl.insert(key, {"nome": f"Nome{key}"})
    
    print("Árvore inicial:")
    for key, value in avl.inorder_items():
        print(f"  {key}")
    
    avl.clear_log()
    
    # Teste 1: Remover nó folha
    print("\nRemoção de nó folha (000002):")
    removed1 = avl.remove("000002")
    print(f"  Removido: {removed1}")
    
    # Teste 2: Remover nó com 1 filho
    print("Remoção de nó com 1 filho (000008 após inserir 000009):")
    avl.insert("000009", {"nome": "Nome000009"})
    removed2 = avl.remove("000008")
    print(f"  Removido: {removed2}")
    
    # Teste 3: Remover nó com 2 filhos
    print("Remoção de nó com 2 filhos (000003):")
    removed3 = avl.remove("000003")
    print(f"  Removido: {removed3}")
    
    summary = avl.summary("sum")
    remove_metrics = summary.get("remove", {})
    
    print(f"\nMétricas de remoção:")
    print(f"  - Comparações: {remove_metrics.get('comparisons', 0)}")
    print(f"  - Visitas de nós: {remove_metrics.get('node_visits', 0)}")
    print(f"  - Rotações: {remove_metrics.get('rotations', 0)}")
    print(f"  - Shifts: {remove_metrics.get('shifts', 0)} (substituições de chave/valor)")
    
    print("\nÁrvore final:")
    for key, value in avl.inorder_items():
        print(f"  {key}")
    print()

def test_avl_edge_cases():
    """Testa casos extremos da AVL."""
    print("=== Teste de Casos Extremos AVL ===")
    
    # Árvore vazia
    avl_empty = AVLTreeDS()
    avl_empty.clear_log()
    
    result = avl_empty.search("000001")
    removed = avl_empty.remove("000001")
    
    print(f"Busca em árvore vazia: {'Encontrado' if result else 'Não encontrado'}")
    print(f"Remoção em árvore vazia: {'Sucesso' if removed else 'Falhou'}")
    
    # Árvore com um elemento
    avl_single = AVLTreeDS()
    avl_single.insert("000001", {"nome": "Único"})
    avl_single.clear_log()
    
    found = avl_single.search("000001")
    removed = avl_single.remove("000001")
    
    print(f"Busca em árvore com 1 elemento: {'Encontrado' if found else 'Não encontrado'}")
    print(f"Remoção em árvore com 1 elemento: {'Sucesso' if removed else 'Falhou'}")
    
    # Verificar se árvore ficou vazia
    final_search = avl_single.search("000001")
    print(f"Busca após remoção: {'Encontrado' if final_search else 'Não encontrado'}")
    print()

if __name__ == "__main__":
    test_avl_basic_functionality()
    test_avl_balance_and_rotations()
    test_avl_search_performance()
    test_avl_removal_cases()
    test_avl_edge_cases()
    
    print("=== Teste com Dados Reais AVL ===")
    # Teste rápido com dados reais
    avl = AVLTreeDS()
    avl.carregar_dados(100)
    avl.print_summary('sum')
