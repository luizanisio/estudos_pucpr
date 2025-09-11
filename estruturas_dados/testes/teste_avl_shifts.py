#!/usr/bin/env python3
"""
Teste específico para verificar contagem de shifts na remoção AVL.
"""
# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

from util_estrutura import AVLTreeDS

def test_avl_remove_shifts():
    """Testa contagem específica de shifts na remoção."""
    print("=== Teste de Shifts na Remoção AVL ===")
    
    avl = AVLTreeDS()
    
    # Insere alguns elementos
    avl.insert("000005", {"nome": "E"})
    avl.insert("000003", {"nome": "C"})  
    avl.insert("000007", {"nome": "G"})
    avl.insert("000002", {"nome": "B"})
    avl.insert("000004", {"nome": "D"})
    avl.insert("000006", {"nome": "F"})
    avl.insert("000008", {"nome": "H"})
    
    print("Árvore montada com 7 nós")
    print("Items em ordem:")
    for key, value in avl.inorder_items():
        print(f"  {key}: {value['nome']}")
    
    # Limpa log para contar apenas a remoção
    avl.clear_log()
    
    # Remove nó com 2 filhos (deve fazer substituição = 2 shifts)
    print(f"\nRemovendo nó 000005 (raiz com 2 filhos)...")
    result = avl.remove("000005")
    print(f"Removido: {result}")
    
    print("Árvore após remoção:")
    for key, value in avl.inorder_items():
        print(f"  {key}: {value['nome']}")
    
    summary = avl.summary("sum")
    remove_metrics = summary.get("remove", {})
    
    print(f"\nMétricas da remoção:")
    print(f"  - Comparações: {remove_metrics.get('comparisons', 0)}")
    print(f"  - Visitas de nós: {remove_metrics.get('node_visits', 0)}")
    print(f"  - Shifts: {remove_metrics.get('shifts', 0)} (esperado: 2 - substituição key/value)")
    print(f"  - Rotações: {remove_metrics.get('rotations', 0)}")
    print(f"  - Mem moves: {remove_metrics.get('mem_moves', 0)}")
    print()

def test_avl_comprehensive():
    """Teste mais abrangente da AVL."""
    print("=== Teste Abrangente AVL ===")
    
    avl = AVLTreeDS()
    avl.carregar_dados(50)  # Usa dados menores para análise
    
    print("Dados carregados. Executando operações...")
    avl.remover_dados(10)
    avl.buscar_dados(10)
    
    avl.print_summary('sum')

if __name__ == "__main__":
    test_avl_remove_shifts()
    test_avl_comprehensive()
