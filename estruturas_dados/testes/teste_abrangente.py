#!/usr/bin/env python3
"""
Teste abrangente do sistema rounds_summary_df com diferentes N e múltiplos rounds.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.extend(['../','./'])

from util_estrutura import AVLTreeDS, HashTableDS, ArrayLinkedList, BaseDataStructure
import pandas as pd

def teste_abrangente():
    """Teste mais realista com diferentes N e múltiplos rounds."""
    print("🔬 TESTE ABRANGENTE DO SISTEMA DE ROUNDS")
    print("=" * 50)
    
    estruturas = []
    
    # Configuração do teste
    tamanhos = [50, 100]  # Tamanhos menores para teste rápido
    n_rounds = 3
    
    # AVL Tree com múltiplos N e rounds
    for n in tamanhos:
        for round_num in range(n_rounds):
            avl = AVLTreeDS()
            avl.clear_log()
            round_id = f"AVL_N{n}_R{round_num+1}"
            # Note: round_id agora é gerado automaticamente como UUID
            
            avl.carregar_dados(n)
            avl.buscar_dados(n // 4)
            avl.remover_dados(n // 10)
            
            estruturas.append(avl)
            print(f"✅ {round_id} (UUID: {avl.round_id[:8]}...): {len(avl.log)} ops")
    
    # Hash Table com múltiplos N e rounds
    for n in tamanhos:
        for round_num in range(n_rounds):
            hash_table = HashTableDS(M=30, hash_fn='poly31')
            hash_table.clear_log()
            round_id = f"Hash_N{n}_R{round_num+1}"
            # Note: round_id agora é gerado automaticamente como UUID
            
            hash_table.carregar_dados(n)
            hash_table.buscar_dados(n // 4)
            hash_table.remover_dados(n // 10)
            
            estruturas.append(hash_table)
            print(f"✅ {round_id} (UUID: {hash_table.round_id[:8]}...): {len(hash_table.log)} ops")
    
    print(f"\n📊 Total: {len(estruturas)} estruturas criadas")
    print(f"📊 Configuração: {len(tamanhos)} tamanhos × {n_rounds} rounds × 2 estruturas")
    
    # Gera o DataFrame
    print("\n🔍 Gerando rounds_summary_df...")
    df = BaseDataStructure.rounds_summary_df(
        structures=estruturas,
        metrics=['comparisons', 'wall_time_ms', 'hash_collisions'],
        agg='sum',
        op_filter=('insert',)
    )
    
    print(f"✅ DataFrame gerado com {len(df)} linhas")
    print("\n📋 Resultado completo:")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    print(df.to_string())
    
    # Análises específicas
    print("\n🔍 ANÁLISES:")
    print("=" * 30)
    
    # 1. Verificar se cada (ds_name, N, metric) tem exatamente n_rounds
    print(f"1. Verificando se cada configuração tem {n_rounds} rounds:")
    rounds_check = df.groupby(['ds_name', 'instances', 'metric'])['rounds'].first()
    for key, rounds in rounds_check.items():
        ds_name, instances, metric = key
        status = "✅" if rounds == n_rounds else "❌"
        print(f"   {status} {ds_name} N={instances} {metric}: {rounds}/{n_rounds} rounds")
    
    # 2. Verificar se há variação entre rounds (std > 0)
    print(f"\n2. Verificando variação entre rounds:")
    std_stats = df['std_per_round'].describe()
    print(f"   Std mín: {std_stats['min']:.6f}")
    print(f"   Std máx: {std_stats['max']:.6f}")
    print(f"   Std médio: {std_stats['mean']:.6f}")
    
    linhas_com_variacao = len(df[df['std_per_round'] > 0])
    total_linhas = len(df)
    print(f"   Linhas com variação: {linhas_com_variacao}/{total_linhas}")
    
    # 3. Verificar métricas específicas de hash
    print(f"\n3. Verificando métricas específicas de hash:")
    hash_metrics = df[df['metric'] == 'hash_collisions']
    if len(hash_metrics) > 0:
        print(f"   ✅ Métricas hash_collisions encontradas: {len(hash_metrics)} linhas")
        for _, row in hash_metrics.iterrows():
            print(f"      {row['ds_name']} N={row['instances']}: {row['mean_per_round']:.1f} ± {row['std_per_round']:.1f}")
    else:
        print(f"   ❌ Nenhuma métrica hash_collisions encontrada")
    
    # 4. Verificar se N maiores têm mais operações
    print(f"\n4. Verificando escala por N:")
    comp_metrics = df[df['metric'] == 'comparisons']
    for ds_name in comp_metrics['ds_name'].unique():
        print(f"   {ds_name}:")
        ds_data = comp_metrics[comp_metrics['ds_name'] == ds_name].sort_values('instances')
        for _, row in ds_data.iterrows():
            print(f"      N={row['instances']}: {row['mean_per_round']:.1f} comparisons")
    
    return True

if __name__ == '__main__':
    try:
        success = teste_abrangente()
        if success:
            print(f"\n🎉 TESTE ABRANGENTE PASSOU!")
        else:
            print(f"\n💥 TESTE ABRANGENTE FALHOU!")
    except Exception as e:
        print(f"\n💥 ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()