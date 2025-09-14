#!/usr/bin/env python3
"""
Teste específico para validar a implementação da estrutura HashTableDS.
"""
# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_estrutura import HashTableDS

def test_hash_basic_functionality():
    """Testa funcionalidade básica da HashTable."""
    print("=== Teste de Funcionalidade Básica HashTable ===")
    
    # Teste com encadeamento
    hash_chain = HashTableDS(M=10, mode="chaining")
    
    # Teste de inserção
    result1 = hash_chain.insert("000001", {"nome": "Ana", "idade": 25})
    result2 = hash_chain.insert("000002", {"nome": "Bruno", "idade": 30})
    result3 = hash_chain.insert("000011", {"nome": "Carlos", "idade": 35})  # pode colidir com 000001
    result4 = hash_chain.insert("000001", {"nome": "Ana2", "idade": 26})  # duplicata
    
    print(f"Inserção 000001: {result1} (esperado: True)")
    print(f"Inserção 000002: {result2} (esperado: True)")
    print(f"Inserção 000011: {result3} (esperado: True)")
    print(f"Inserção duplicata: {result4} (esperado: False)")
    
    # Teste de busca
    found1 = hash_chain.search("000001")
    found2 = hash_chain.search("000011")
    found3 = hash_chain.search("000999")  # não existe
    
    print(f"Busca 000001: {found1 is not None} (esperado: True)")
    print(f"Busca 000011: {found2 is not None} (esperado: True)")
    print(f"Busca 000999: {found3 is not None} (esperado: False)")
    
    # Teste de remoção
    removed1 = hash_chain.remove("000001")
    removed2 = hash_chain.remove("000999")  # não existe
    
    print(f"Remoção 000001: {removed1} (esperado: True)")
    print(f"Remoção 000999: {removed2} (esperado: False)")
    
    print(f"Items restantes: {hash_chain.n_items} (esperado: 2)")
    print(f"Load factor: {hash_chain.load_factor():.2f}")
    print()

def test_hash_chaining_metrics():
    """Testa métricas específicas do encadeamento."""
    print("=== Teste de Métricas - Encadeamento ===")
    
    # Tabela pequena para forçar colisões
    hash_table = HashTableDS(M=5, mode="chaining", hash_fn="poly31")
    hash_table.clear_log()
    
    # Insere elementos que devem colidir
    keys = ["000001", "000006", "000011", "000016", "000021"]  # últimos dígitos diferentes
    for key in keys:
        hash_table.insert(key, {"nome": f"Nome{key}"})
    
    summary = hash_table.summary("sum")
    insert_metrics = summary.get("insert", {})
    
    print(f"Métricas de inserção (encadeamento, M=5):")
    print(f"  - Comparações: {insert_metrics.get('comparisons', 0)}")
    print(f"  - Probes: {insert_metrics.get('probes', 0)} (1 por inserção)")
    print(f"  - Hash collisions: {insert_metrics.get('hash_collisions', 0)}")
    print(f"  - Bucket len after (soma): {insert_metrics.get('hash_bucket_len_after', 0)}")
    print(f"  - Shifts: {insert_metrics.get('shifts', 0)} (deveria ser 0 - só append)")
    
    print(f"  - Colisões totais acumuladas: {hash_table.collisions_total}")
    print(f"  - Max chain length: {hash_table.max_chain_length()}")
    print(f"  - Load factor: {hash_table.load_factor():.2f}")
    print()

def test_hash_open_addressing():
    """Testa endereçamento aberto."""
    print("=== Teste de Endereçamento Aberto ===")
    
    # Teste com sondagem linear
    hash_open = HashTableDS(M=7, mode="open", probing="linear", hash_fn="djb2")
    hash_open.clear_log()
    
    # Insere elementos
    keys = ["000001", "000008", "000015"]  # podem colidir dependendo da função hash
    for key in keys:
        result = hash_open.insert(key, {"nome": f"Nome{key}"})
        print(f"Inseriu {key}: {result}")
    
    print("Testando busca...")
    found = hash_open.search("000008")
    print(f"Encontrou 000008: {found is not None}")
    
    summary = hash_open.summary("sum")
    metrics = summary.get("insert", {}).copy()
    metrics.update(summary.get("search", {}))
    
    print(f"\nMétricas de endereçamento aberto:")
    print(f"  - Comparações: {metrics.get('comparisons', 0)}")
    print(f"  - Probes: {metrics.get('probes', 0)}")
    print(f"  - Hash collisions: {metrics.get('hash_collisions', 0)}")
    print(f"  - Cluster len (soma): {metrics.get('hash_cluster_len', 0)}")
    print(f"  - Displacement (soma): {metrics.get('hash_displacement', 0)}")
    print(f"  - Load factor: {hash_open.load_factor():.2f}")
    print()

def test_hash_probing_methods():
    """Testa diferentes métodos de sondagem."""
    print("=== Teste de Métodos de Sondagem ===")
    
    # Teste sondagem quadrática
    hash_quad = HashTableDS(M=11, mode="open", probing="quadratic", c1=1, c2=3)
    hash_quad.clear_log()
    
    # Insere alguns elementos
    for i in range(5):
        key = f"00000{i}"
        hash_quad.insert(key, {"value": i})
    
    summary_quad = hash_quad.summary("sum")
    insert_quad = summary_quad.get("insert", {})
    
    print(f"Sondagem Quadrática (M=11, c1=1, c2=3):")
    print(f"  - Probes: {insert_quad.get('probes', 0)}")
    print(f"  - Cluster len (total): {insert_quad.get('hash_cluster_len', 0)}")
    
    # Teste double hashing
    hash_double = HashTableDS(M=11, mode="open", probing="double", 
                             hash_fn="poly31", hash2_fn="fnv1a")
    hash_double.clear_log()
    
    for i in range(5):
        key = f"00000{i}"
        hash_double.insert(key, {"value": i})
    
    summary_double = hash_double.summary("sum")
    insert_double = summary_double.get("insert", {})
    
    print(f"Double Hashing (M=11, poly31|fnv1a):")
    print(f"  - Probes: {insert_double.get('probes', 0)}")
    print(f"  - Cluster len (total): {insert_double.get('hash_cluster_len', 0)}")
    print()

def test_hash_removal_tombstones():
    """Testa remoção e uso de tombstones."""
    print("=== Teste de Remoção e Tombstones ===")
    
    hash_table = HashTableDS(M=7, mode="open", probing="linear")
    
    # Insere elementos
    keys = ["000001", "000008", "000015", "000022"]
    for key in keys:
        hash_table.insert(key, {"nome": f"Nome{key}"})
    
    print(f"Inseridos {len(keys)} elementos. Load factor: {hash_table.load_factor():.2f}")
    
    # Remove um elemento do meio da sequência
    hash_table.clear_log()
    removed = hash_table.remove("000008")
    print(f"Removeu 000008: {removed}")
    
    # Tenta buscar elemento que estava após o removido
    found = hash_table.search("000015")
    print(f"Ainda encontra 000015: {found is not None}")
    
    # Insere novo elemento (pode reutilizar tombstone)
    hash_table.clear_log()
    inserted = hash_table.insert("000029", {"nome": "Nome000029"})
    print(f"Inseriu 000029: {inserted}")
    
    summary = hash_table.summary("sum")
    insert_metrics = summary.get("insert", {})
    
    print(f"Métricas da inserção pós-remoção:")
    print(f"  - Probes: {insert_metrics.get('probes', 0)}")
    print(f"  - Usou tombstone: {any(r.extras.get('used_tombstone', False) for r in hash_table.log if r.op == 'insert')}")
    print()

def test_hash_functions():
    """Testa diferentes funções hash."""
    print("=== Teste de Funções Hash ===")
    
    test_key = "000123"
    
    # Testa cada função hash
    hash_fns = ["poly31", "fnv1a", "djb2"]
    
    for fn_name in hash_fns:
        hash_table = HashTableDS(M=1000, hash_fn=fn_name)
        
        # Calcula índice para a mesma chave
        idx = hash_table._idx1(test_key)
        print(f"Hash {fn_name} para '{test_key}': índice {idx}")
    
    print()

def test_hash_edge_cases():
    """Testa casos extremos da HashTable."""
    print("=== Teste de Casos Extremos ===")
    
    # Tabela muito pequena
    tiny_hash = HashTableDS(M=2, mode="chaining")
    
    # Insere mais elementos que slots
    for i in range(5):
        key = f"00000{i}"
        result = tiny_hash.insert(key, {"value": i})
        print(f"Inseriu {key} (tabela M=2): {result}")
    
    print(f"Load factor com M=2: {tiny_hash.load_factor():.1f}")
    print(f"Max chain length: {tiny_hash.max_chain_length()}")
    
    # Teste de tabela cheia (endereçamento aberto)
    print("\nTeste tabela cheia (endereçamento aberto):")
    full_hash = HashTableDS(M=3, mode="open", probing="linear")
    
    # Tenta inserir mais que a capacidade
    success_count = 0
    for i in range(5):
        key = f"00000{i}"
        result = full_hash.insert(key, {"value": i})
        if result:
            success_count += 1
        print(f"Inseriu {key}: {result}")
    
    print(f"Inserções bem-sucedidas: {success_count}/5")
    print()

if __name__ == "__main__":
    test_hash_basic_functionality()
    test_hash_chaining_metrics()
    test_hash_open_addressing() 
    test_hash_probing_methods()
    test_hash_removal_tombstones()
    test_hash_functions()
    test_hash_edge_cases()
    
    print("=== Teste com Dados Reais ===")
    # Teste rápido com dados reais
    hash_table = HashTableDS(M=150, mode="chaining")
    hash_table.carregar_dados(100)
    hash_table.print_summary('sum')
