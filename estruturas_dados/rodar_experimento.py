# Adiciona o diretório atual ao path
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util_estrutura import AVLTreeDS, HashTableDS, ArrayLinkedList, BaseDataStructure
from util_graficos import GraficosMetricas
from time import time
import json

"""
ESTRUTURAS TESTADAS:
- AVL Tree (balanceada e não balanceada)
- Hash Tables com 3 tamanhos (M=100, 1000, 5000) e 3 funções hash (poly31, fnv1a, djb2)
  usando encadeamento separado (chaining) para resolução de colisões
- Array Linked Lists (ordenada e não-ordenada)
"""

# Gera dados com diferentes tamanhos
TAMANHOS = [1000, 5000, 10000, 50000, 100000]
M_HASH_TABLE = [100,1000,5000]
N_ROUNDS = 5
PASTA_ROUNDS = './rounds'
os.makedirs(PASTA_ROUNDS, exist_ok=True)

def gerar_experimento_completo():
    """
    Gera experimento completo comparando diferentes estruturas de dados
    com {N_ROUNDS} rounds para cada configuração N × estrutura.
    """
    print("🔬 INICIANDO EXPERIMENTO COMPLETO DE ESTRUTURAS DE DADOS")
    print("=" * 60)
    GraficosMetricas.limpar_pasta_graficos()
    
    # Lista para armazenar todas as estruturas com dados coletados
    lista_metricas = []
    
    # Definição das estruturas a serem testadas
    estruturas = [
        ("AVL Tree balanceada", lambda: AVLTreeDS(balanced=True)),
        ("AVL Tree não balanceada", lambda: AVLTreeDS(balanced=False)),
        ("Array LinkedList Não ordenado", lambda: ArrayLinkedList(sorted_insert=False)),
        ("Array LinkedList Ordenado", lambda: ArrayLinkedList(sorted_insert=True))
    ]
    for h in M_HASH_TABLE:
        estruturas.append((f"Hash Table M={h} poly31", lambda h=h: HashTableDS(M=h, hash_fn='poly31')))
        estruturas.append((f"Hash Table M={h} fnv1a", lambda h=h: HashTableDS(M=h, hash_fn='fnv1a')))
        estruturas.append((f"Hash Table M={h} djb2", lambda h=h: HashTableDS(M=h, hash_fn='djb2')))
    
    # Para debug/testes rápidos: descomente a linha abaixo para testar apenas AVL Trees
    # com parâmetro debug, roda o experimento rápido
    if '-debug' in sys.argv:
        print("⚠️ Modo DEBUG ativado: executando experimento rápido com apenas 2 estruturas e 2 tamanhos")
        global N_ROUNDS, TAMANHOS
        N_ROUNDS = 2
        TAMANHOS = [1000, 5000]
        estruturas = estruturas[:3]  # Apenas as 2 AVL Trees e 1 ArrayLinkedList

    if '-limpar' in sys.argv:
        print("⚠️ Limpar cache: remove métricas antigas na pasta rounds")
        for f in os.listdir(PASTA_ROUNDS):
            if f.endswith('.json'):
                os.remove(os.path.join(PASTA_ROUNDS, f))
        print("   ✅ Cache limpo com sucesso!")
    
    print(f"📊 Configuração do experimento:")
    print(f"  - {len(estruturas)} estruturas diferentes")
    print(f"  - 2 AVL Trees (balanceada e não-balanceada)")
    print(f"  - {3*len(M_HASH_TABLE)} Hash Tables: {len(M_HASH_TABLE)} tamanhos de M {M_HASH_TABLE} × 3 funções hash (poly31,fnv1a,djb2)")
    print(f"    usando encadeamento separado (chaining) para resolução de colisões")
    print(f"  - 2 Array Linked Lists (ordenada e não-ordenada)")
    print(f"  - {len(TAMANHOS)} tamanhos: {TAMANHOS}")
    print(f"  - {N_ROUNDS} rounds por configuração")
    print(f"  - Total: {len(estruturas) * len(TAMANHOS) * N_ROUNDS} execuções")
    print()

    
    # Coleta dados para todas as combinações
    total_execucoes = len(estruturas) * len(TAMANHOS) * N_ROUNDS
    execucao_atual = 0
    
    for i, (nome_estrutura, factory_estrutura) in enumerate(estruturas):
        print(f"🔧 ESTRUTURA {i+1}/{len(estruturas)}: {nome_estrutura}")
        
        for n in TAMANHOS:
            print(f"  📏 N = {n:,} elementos")

            # verifica se todos os rounds estão em disco e usa os dados carregados
            gerar_arq_metricas = lambda rn,nm, _n:os.path.join(PASTA_ROUNDS,f'metrics_{nm.replace(" ","_")}_N{_n}_round{rn}.json')
            metricas_disco = []
            for round_num in range(N_ROUNDS):
                arq_metricas = gerar_arq_metricas(round_num, nome_estrutura, n)
                if os.path.exists(arq_metricas):
                    print(f"    ✅ Round {round_num+1}/{N_ROUNDS} | {nome_estrutura} N = {n} | [já existente, carregando...]")
                    # Carrega métricas do arquivo JSON
                    try:
                        with open(arq_metricas, 'r') as f:
                            metricas_json = json.load(f)
                        metricas_disco.append(metricas_json)
                    except Exception as e:
                        print(f"    ❌ Erro ao carregar {arq_metricas}: {e}")
                        metricas_disco = []
                        break
                else:
                    metricas_disco = []
                    break

            if len(metricas_disco) == N_ROUNDS:
                print(f"    🎉 Todos os {N_ROUNDS} rounds já existem em disco. Usando dados carregados.")
                lista_metricas.extend(metricas_disco)
                continue  # pula para o próximo tamanho n
            
            for round_num in range(N_ROUNDS):
                execucao_atual += 1
                progresso = (execucao_atual / total_execucoes) * 100
                
                print(f"    🔄 Round {round_num+1}/{N_ROUNDS} | {nome_estrutura} N = {n} | [{progresso:.1f}%]")
                
                # Cria nova instância da estrutura
                estrutura:BaseDataStructure = factory_estrutura()
                estrutura.clear_log()  # Limpa logs anteriores
                                
                # Executa operações
                estrutura.carregar_dados(n)        # INSERTs
                estrutura.buscar_dados(n // 4)     # SEARCHs (25% do total)
                estrutura.remover_dados(n // 10)   # REMOVEs (10% do total)
                estrutura.descarregar_dados()      # retira o dataset da memória
                
                # Adiciona à lista
                metricas = estrutura.export_metrics_json()
                # Salva métricas em arquivo JSON para possível reuso futuro
                arq_metricas = gerar_arq_metricas(round_num, nome_estrutura, n)
                try:
                    with open(arq_metricas, 'w') as f:
                        json.dump(metricas, f, indent=2)
                    print(f"      💾 Métricas salvas em {arq_metricas}")
                except Exception as e:
                    print(f"      ❌ Erro ao salvar métricas em {arq_metricas}: {e}")
                    exit(1)
                lista_metricas.append(metricas)
    
    print("\n✅ Coleta de dados concluída!")
    print(f"📊 {len(lista_metricas)} estruturas prontas para análise")
    
    return lista_metricas, estruturas

def gerar_graficos_comparativos(lista_metricas):
    """
    Gera gráficos comparativos com um gráfico por métrica.
    Cada gráfico compara todas as estruturas para uma única métrica.
    """
    print("\n📈 GERANDO GRÁFICOS COMPARATIVOS...")
    print("=" * 40)
    
    # Converte estruturas para o formato de métricas JSON ou utiliza as que foram recuperadas
   
    gm = GraficosMetricas()
    caminhos_gerados = []
    
    # Definição das métricas principais para todas as estruturas
    metricas_principais = [
        ('comparisons', 'Comparações', ('insert', 'search', 'remove')),
        ('node_visits', 'Visitas de Nós (Árvores/Listas)', ('insert', 'search', 'remove')),
        ('wall_time_ms', 'Tempo de Execução (ms)', ('insert', 'search', 'remove')),
        ('mem_moves', 'Movimentações de Memória', ('insert', 'search', 'remove')),
        ('proc_time_ms', 'Tempo de CPU (ms)', ('insert', 'search', 'remove'))
    ]
    
    # Gera um gráfico por métrica principal
    print("📊 Gerando gráficos individuais por métrica...")
    for i, (metrica, titulo_metrica, operacoes) in enumerate(metricas_principais, 1):
        for escala in ['linear', 'log']:
            print(f"  {i}. {titulo_metrica}. {escala}...")
            
            # Filtra métricas para estruturas que suportam esta métrica
            metricas_filtradas = []
            for metrica_json in lista_metricas:
                # Verifica se a métrica json alguma estrutura correspondente ignora esta métrica
                if metrica not in metrica_json.get('metrics_out',[]):
                   metricas_filtradas.append(metrica_json)
            
            # Gera gráfico comparativo para esta métrica
            caminho = gm.plotar_metricas(
                metrics_data=metricas_filtradas,
                metrics=[metrica],  # Uma métrica por gráfico
                agg='sum',
                escala=escala,
                op_filter=operacoes,
                titulo_personalizado=f'{titulo_metrica} - Comparação entre Estruturas'
            )
            caminhos_gerados.append(caminho)
    
    # Métricas específicas para análise detalhada de operações
    print("📊 Gerando gráficos específicos por operação...")
    
    for escala in ['linear', 'log']:
        print(f"  5. Tempo de Execução (ms). {escala}...")
        caminho_time = gm.plotar_metricas(
            metrics_data=lista_metricas,
            metrics=['wall_time_ms'],
            agg='sum',
            escala=escala,
            op_filter=('insert', 'search', 'remove'),
            titulo_personalizado='Tempo de Execução (ms) - Todas as Operações'
        )
        caminhos_gerados.append(caminho_time)
        # Análise específica de inserções
        print(f"  6. Comparações em Inserções. {escala}...")
        caminho_insert = gm.plotar_metricas(
            metrics_data=lista_metricas,
            metrics=['comparisons'],
            agg='sum',
            escala=escala,
            op_filter=('insert',),
            titulo_personalizado='Comparações - Operações de Inserção'
        )
        caminhos_gerados.append(caminho_insert)
        
        # Análise específica de buscas
        print(f"  7. Comparações em Buscas. {escala}...")
        caminho_search = gm.plotar_metricas(
            metrics_data=lista_metricas,
            metrics=['comparisons'],
            agg='sum',
            escala=escala,
            op_filter=('search',),
            titulo_personalizado='Comparações - Operações de Busca'
        )
        caminhos_gerados.append(caminho_search)
    
        # Separar métricas de estruturas hash para análise específica
        hash_metricas = []
        for metrica_json in lista_metricas:
            # Verifica se é uma estrutura hash
            if 'HashTable' in metrica_json.get('ds_name', ''):
                hash_metricas.append(metrica_json)
        
        # Gráficos específicos para Hash Tables (se existirem)
        if hash_metricas:
            print(f"📊 Gerando gráficos específicos para Hash Tables.{escala}...")
            
            # Métricas específicas de hash tables
            metricas_hash = [
                ('hash_collisions', 'Colisões de Hash', ('insert', 'search')),
                ('hash_bucket_len_after', 'Tamanho dos Buckets após Inserção', ('insert',)),
                ('probes', 'Tentativas de Acesso aos Buckets', ('insert', 'search'))
            ]
            
            for j, (metrica_hash, titulo_hash, ops_hash) in enumerate(metricas_hash, 8):
                print(f"  {j}. {titulo_hash}...")
                
                # Gera gráfico específico para hash tables
                caminho_hash = gm.plotar_metricas(
                    metrics_data=hash_metricas,  # Apenas métricas de hash tables
                    metrics=[metrica_hash],
                    agg='sum',
                    escala=escala,
                    op_filter=ops_hash,
                    titulo_personalizado=f'{titulo_hash} - Hash Tables'
                )
                caminhos_gerados.append(caminho_hash)
    
    return caminhos_gerados

# Execução principal
if __name__ == "__main__":
    inicio = time()
    # limpando pasta de gráficos antigos
    GraficosMetricas.limpar_pasta_graficos()
    # Gera experimento
    lista_metricas, estruturas = gerar_experimento_completo()
    
    # Gera gráficos
    caminhos = gerar_graficos_comparativos(lista_metricas)

    print("\n🎉 EXPERIMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("📈 Gráficos gerados:")
    for i, caminho in enumerate(caminhos, 1):
        print(f"  {i}. {caminho}")
    
    print(f"\n📁 Verifique a pasta './graficos' para ver todos os arquivos gerados")
    print(f"📊 Total de estruturas analisadas: {len(lista_metricas)}")
    
    # Estatísticas do experimento
    print(f"\n📋 ESTATÍSTICAS DO EXPERIMENTO:")
    print(f"  - Estruturas testadas: {len(estruturas)}")
    print(f"    • 2 AVL Trees (balanceada e não-balanceada)")
    print(f"    • {3*len(M_HASH_TABLE)} Hash Tables ({len(M_HASH_TABLE)} valores de M {M_HASH_TABLE} × 3 funções hash) usando encadeamento separado")
    print(f"    • 2 Array Linked Lists")
    print(f"  - Tamanhos testados: {len(TAMANHOS)} {TAMANHOS}")
    print(f"  - Rounds por configuração: {N_ROUNDS}")
    print(f"  - Total de execuções: {len(lista_metricas)}")
    print(f"  - Gráficos gerados: {len(caminhos)} (um por métrica)")
    print(f"  - Métricas principais: {len(caminhos)} gráficos comparando todas as estruturas")   
    print('|' * 80)
    print(f'Tempo de geração do experimento: {time() - inicio:.2f} segundos')
    
    print("\nObrigado por utilizar o framework de experimentos de estruturas de dados do grupo 5!")