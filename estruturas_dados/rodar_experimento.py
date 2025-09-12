# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util_estrutura import AVLTreeDS, HashTableDS, ArrayLinkedList, BaseDataStructure
from util_graficos import GraficosMetricas

"""
MODIFICAÇÕES NA GERAÇÃO DE GRÁFICOS:
- Cada gráfico agora mostra UMA métrica comparando TODAS as estruturas
- 5 gráficos principais: comparisons, node_visits, wall_time_ms, mem_moves, proc_time_ms
- 2 gráficos de operações específicas: inserções e buscas (comparisons)
- 3 gráficos específicos para Hash Tables: hash_collisions, hash_cluster_len, probes
- Total: 10 gráficos individuais
"""

def gerar_experimento_completo():
    """
    Gera experimento completo comparando diferentes estruturas de dados
    com 5 rounds para cada configuração N × estrutura.
    """
    print("🔬 INICIANDO EXPERIMENTO COMPLETO DE ESTRUTURAS DE DADOS")
    print("=" * 60)
    GraficosMetricas.limpar_pasta_graficos()
    
    # Lista para armazenar todas as estruturas com dados coletados
    lista_estruturas = []
    
    # Definição das estruturas a serem testadas
    estruturas = [
        ("AVL Tree", lambda: AVLTreeDS()),
        ("Hash Table M=50 Quadratic", lambda: HashTableDS(M=50, probing='quadratic')),
        ("Hash Table M=100 Quadratic", lambda: HashTableDS(M=100, probing='quadratic')),
        ("Hash Table M=150 Quadratic", lambda: HashTableDS(M=150, probing='quadratic')),
        ("Hash Table M=50 Linear", lambda: HashTableDS(M=50, probing='linear')),
        ("Hash Table M=100 Linear", lambda: HashTableDS(M=100, probing='linear')),
        ("Hash Table M=150 Linear", lambda: HashTableDS(M=150, probing='linear')),
        ("Array LinkedList Unsorted", lambda: ArrayLinkedList()),
        ("Array LinkedList Sorted", lambda: ArrayLinkedList(sorted_insert=True))
    ]
    
    # Gera dados com diferentes tamanhos
    tamanhos = list(range(1000, 10001, 1000))  # 1K, 2K, ..., 10K
    n_rounds = 5
    
    print(f"📊 Configuração do experimento:")
    print(f"  - {len(estruturas)} estruturas diferentes")
    print(f"  - {len(tamanhos)} tamanhos: {tamanhos}")
    print(f"  - {n_rounds} rounds por configuração")
    print(f"  - Total: {len(estruturas) * len(tamanhos) * n_rounds} execuções")
    print()
    
    # Coleta dados para todas as combinações
    total_execucoes = len(estruturas) * len(tamanhos) * n_rounds
    execucao_atual = 0
    
    for i, (nome_estrutura, factory_estrutura) in enumerate(estruturas):
        print(f"🔧 ESTRUTURA {i+1}/{len(estruturas)}: {nome_estrutura}")
        
        for n in tamanhos:
            print(f"  📏 N = {n:,} elementos")
            
            for round_num in range(n_rounds):
                execucao_atual += 1
                progresso = (execucao_atual / total_execucoes) * 100
                
                print(f"    🔄 Round {round_num+1}/{n_rounds} [{progresso:.1f}%]")
                
                # Cria nova instância da estrutura
                estrutura = factory_estrutura()
                estrutura.clear_log()  # Limpa logs anteriores
                
                # Executa operações
                estrutura.carregar_dados(n)        # INSERTs
                estrutura.buscar_dados(n // 4)     # SEARCHs (25% do total)
                estrutura.remover_dados(n // 10)   # REMOVEs (10% do total)
                
                # Adiciona à lista
                lista_estruturas.append(estrutura)
    
    print("\n✅ Coleta de dados concluída!")
    print(f"📊 {len(lista_estruturas)} estruturas prontas para análise")
    
    return lista_estruturas, estruturas

def gerar_graficos_comparativos(lista_estruturas):
    """
    Gera gráficos comparativos com um gráfico por métrica.
    Cada gráfico compara todas as estruturas para uma única métrica.
    """
    print("\n📈 GERANDO GRÁFICOS COMPARATIVOS...")
    print("=" * 40)
    
    gm = GraficosMetricas()
    caminhos_gerados = []
    
    # Definição das métricas principais para todas as estruturas
    metricas_principais = [
        ('comparisons', 'Comparações', ('insert', 'search', 'remove')),
        ('node_visits', 'Visitas de Nós', ('insert', 'search', 'remove')),
        ('wall_time_ms', 'Tempo de Execução (ms)', ('insert', 'search', 'remove')),
        ('mem_moves', 'Movimentações de Memória', ('insert', 'search', 'remove')),
        ('proc_time_ms', 'Tempo de CPU (ms)', ('insert', 'search', 'remove'))
    ]
    
    # Gera um gráfico por métrica principal
    print("📊 Gerando gráficos individuais por métrica...")
    for i, (metrica, titulo_metrica, operacoes) in enumerate(metricas_principais, 1):
        print(f"  {i}. {titulo_metrica}...")
        
        # Gera gráfico comparativo para esta métrica
        caminho = gm.plotar_metricas(
            structures=lista_estruturas,
            metrics=[metrica],  # Uma métrica por gráfico
            agg='sum',
            escala='linear',
            op_filter=operacoes,
            titulo_personalizado=f'{titulo_metrica} - Comparação entre Estruturas'
        )
        caminhos_gerados.append(caminho)
    
    # Métricas específicas para análise detalhada de operações
    print("📊 Gerando gráficos específicos por operação...")
    
    # Análise específica de inserções
    print("  6. Comparações em Inserções...")
    caminho_insert = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['comparisons'],
        agg='sum',
        escala='linear',
        op_filter=('insert',),
        titulo_personalizado='Comparações - Operações de Inserção'
    )
    caminhos_gerados.append(caminho_insert)
    
    # Análise específica de buscas
    print("  7. Comparações em Buscas...")
    caminho_search = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['comparisons'],
        agg='sum',
        escala='linear',
        op_filter=('search',),
        titulo_personalizado='Comparações - Operações de Busca'
    )
    caminhos_gerados.append(caminho_search)
    
    # Separar estruturas hash para análise específica
    hash_structures = [
        e for e in lista_estruturas
        if 'HashTable' in e.__class__.__name__
    ]
    
    # Gráficos específicos para Hash Tables (se existirem)
    if hash_structures:
        print("📊 Gerando gráficos específicos para Hash Tables...")
        
        # Métricas específicas de hash tables
        metricas_hash = [
            ('hash_collisions', 'Colisões de Hash', ('insert', 'search')),
            ('hash_cluster_len', 'Comprimento de Clusters', ('insert', 'search')),
            ('probes', 'Tentativas de Sondagem', ('insert', 'search'))
        ]
        
        for j, (metrica_hash, titulo_hash, ops_hash) in enumerate(metricas_hash, 8):
            print(f"  {j}. {titulo_hash}...")
            
            # Gera gráfico específico para hash tables
            caminho_hash = gm.plotar_metricas(
                structures=hash_structures,  # Apenas hash tables
                metrics=[metrica_hash],
                agg='sum',
                escala='linear',
                op_filter=ops_hash,
                titulo_personalizado=f'{titulo_hash} - Hash Tables'
            )
            caminhos_gerados.append(caminho_hash)
    
    return caminhos_gerados

# Execução principal
if __name__ == "__main__":
    # limpando pasta de gráficos antigos
    GraficosMetricas.limpar_pasta_graficos()
    # Gera experimento
    lista_estruturas, estruturas = gerar_experimento_completo()
    
    # Gera gráficos
    caminhos = gerar_graficos_comparativos(lista_estruturas)

    print("\n🎉 EXPERIMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("📈 Gráficos gerados:")
    for i, caminho in enumerate(caminhos, 1):
        print(f"  {i}. {caminho}")
    
    print(f"\n📁 Verifique a pasta './graficos' para ver todos os arquivos gerados")
    print(f"📊 Total de estruturas analisadas: {len(lista_estruturas)}")
    
    # Estatísticas do experimento
    print(f"\n📋 ESTATÍSTICAS DO EXPERIMENTO:")
    print(f"  - Estruturas testadas: {len(estruturas)}")
    print(f"  - Tamanhos testados: {len(list(range(1000, 10001, 1000)))}")
    print(f"  - Rounds por configuração: 5")
    print(f"  - Total de execuções: {len(lista_estruturas)}")
    print(f"  - Gráficos gerados: {len(caminhos)} (um por métrica)")
    print("  - Métricas principais: 5 gráficos comparando todas as estruturas")
    print("  - Análises específicas: 2 gráficos de operações individuais")
    
    # Contabiliza gráficos de hash tables se existirem
    hash_count = sum(1 for e in lista_estruturas if 'HashTable' in e.__class__.__name__)
    if hash_count > 0:
        print("  - Hash Tables: 3 gráficos específicos (apenas estruturas hash)")
