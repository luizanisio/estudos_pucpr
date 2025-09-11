# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util_estrutura import AVLTreeDS, HashTableDS, ArrayLinkedList, BaseDataStructure
from util_graficos import GraficosMetricas

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
        ("Hash Table M=1000 Quadratic", lambda: HashTableDS(M=1000, probing='quadratic')),
        ("Hash Table M=100 Linear", lambda: HashTableDS(M=100, probing='linear')), 
        ("Hash Table M=50 Linear", lambda: HashTableDS(M=50, probing='linear')), 
        ("Hash Table M=1000 Linear", lambda: HashTableDS(M=1000, probing='linear')),
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
    """Gera diferentes tipos de gráficos comparativos."""
    print("\n📈 GERANDO GRÁFICOS COMPARATIVOS...")
    print("=" * 40)
    
    gm = GraficosMetricas()

    caminhos_gerados = []
    
    # 1. Gráfico geral: Comparações, visitas de nó e tempo
    print("📊 1. Métricas gerais de eficiência...")
    caminho1 = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['comparisons', 'node_visits', 'wall_time_ms'],
        agg='sum',
        escala='linear',
        op_filter=('insert', 'search', 'remove'),
        titulo_personalizado='Eficiência Geral - Comparações, Visitas e Tempo'
    )
    caminhos_gerados.append(caminho1)
    
    # 2. Gráfico de movimentações de memória e CPU
    print("📊 2. Métricas de sistema (CPU e memória)...")
    caminho2 = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['mem_moves', 'proc_time_ms'],
        agg='sum',
        escala='linear',
        op_filter=('insert', 'search', 'remove'),
        titulo_personalizado='Movimentações de Memória e Tempo de CPU'
    )
    caminhos_gerados.append(caminho2)
    
    # 3. Análise específica de inserções
    print("📊 3. Análise específica - Inserções...")
    caminho3 = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['comparisons', 'node_visits', 'mem_moves'],
        agg='sum',
        escala='linear',
        op_filter=('insert',),
        titulo_personalizado='Eficiência de Inserção - Comparações, Visitas e Movimentações'
    )
    caminhos_gerados.append(caminho3)
    
    # 4. Análise específica de buscas
    print("📊 4. Análise específica - Buscas...")
    caminho4 = gm.plotar_metricas(
        structures=lista_estruturas,
        metrics=['comparisons', 'node_visits', 'wall_time_ms'],
        agg='sum',
        escala='linear',
        op_filter=('search',),
        titulo_personalizado='Eficiência de Busca - Comparações, Visitas e Tempo'
    )
    caminhos_gerados.append(caminho4)
    
    # 5. Métricas específicas para estruturas Hash
    print("📊 5. Métricas específicas - Hash Tables...")
    hash_structures = [
        e for e in lista_estruturas 
        if 'HashTable' in e.__class__.__name__
    ]
    
    if hash_structures:
        caminho5 = gm.plotar_metricas(
            structures=hash_structures,
            metrics=['hash_collisions', 'hash_cluster_len', 'probes'],
            agg='sum',
            escala='linear',
            op_filter=('insert', 'search'),
            titulo_personalizado='Métricas Específicas - Hash Tables (Colisões, Clusters, Probes)'
        )
        caminhos_gerados.append(caminho5)
    
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
    print(f"  - Gráficos gerados: {len(caminhos)}")
