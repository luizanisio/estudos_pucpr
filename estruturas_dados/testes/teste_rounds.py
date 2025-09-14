#!/usr/bin/env python3
"""
Teste para verificar se o rounds_summary_df está funcionando corretamente
com o novo sistema de round_id.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_estrutura import AVLTreeDS, HashTableDS, ArrayLinkedList, BaseDataStructure
import pandas as pd

def teste_rounds_summary():
    """Testa se as métricas por round estão sendo calculadas corretamente."""
    print("🧪 TESTE DO SISTEMA DE ROUNDS")
    print("=" * 50)
    
    # Cria estruturas de teste
    estruturas = []
    
    # 2 AVL Trees com 2 rounds cada
    for N in (1000,10000):
       for round_num in range(2):
        avl = AVLTreeDS()
        avl.clear_log()
        
        # Executa operações para este round
        avl.carregar_dados(N)
        avl.buscar_dados(250)
        avl.remover_dados(100)
        
        estruturas.append(avl)
        print(f"✅ Criado {avl.round_id}: {len(avl.log)} operações registradas")
    
    # 2 Hash Tables com 2 rounds cada
    for round_num in range(2):
        hash_table = HashTableDS(M=50, hash_fn='poly31')
        hash_table.clear_log()
        
        # Executa operações para este round
        hash_table.carregar_dados(1000)
        hash_table.buscar_dados(250)
        hash_table.remover_dados(10)
        
        estruturas.append(hash_table)
        print(f"✅ Criado {hash_table.round_id}: {len(hash_table.log)} operações registradas")
    
    print(f"\n📊 Total: {len(estruturas)} estruturas criadas")
    
    # Testa o rounds_summary_df
    print("\n🔍 Testando rounds_summary_df...")
    
    try:
        df = BaseDataStructure.rounds_summary_df(
            structures=estruturas,
            metrics=['comparisons', 'wall_time_ms'],
            agg='sum',
            op_filter=('insert',)
        )
        
        print(f"✅ DataFrame gerado com {len(df)} linhas")
        print("\n📋 Resultado:")
        print(df.to_string())
        
        # Verifica se há múltiplos rounds por estrutura
        print("\n🔍 Verificando rounds por estrutura:")
        rounds_por_estrutura = df.groupby(['ds_name', 'instances', 'metric'])['rounds'].first()
        for key, rounds in rounds_por_estrutura.items():
            ds_name, instances, metric = key
            print(f"  - {ds_name} N={instances} {metric}: {rounds} rounds")
            
        # Verifica se os desvios-padrão foram calculados
        print("\n🔍 Verificando desvios-padrão:")
        std_nao_zero = df[df['std_per_round'] > 0]
        if len(std_nao_zero) > 0:
            print(f"✅ {len(std_nao_zero)} métricas têm std > 0 (variação entre rounds)")
        else:
            print("⚠️  Todas as métricas têm std = 0 (sem variação entre rounds)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar DataFrame: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success2 = teste_rounds_summary()
    
    if  success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n💥 ALGUNS TESTES FALHARAM!")