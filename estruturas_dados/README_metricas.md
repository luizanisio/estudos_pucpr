📋 Descrição das métricas
=================================================

### **Classe OpRecord**:
Métricas de tempo e sistema:

- **wall_time_ms**: tempo total decorrido durante a operação
- **proc_time_ms**: tempo de processamento usado pela CPU
- **cpu_user_ms**: tempo gasto executando código do programa
- **cpu_system_ms**: tempo gasto em operações do sistema
- **rss_mb**: quantidade de memória RAM ocupada (MB)
- **tracemalloc_peak_kb**: pico de memória alocada pelo Python (KB)

Contadores de operações básicas:
- **comparisons**: quantas vezes duas chaves foram comparadas
- **swaps**: quantas trocas de posição entre elementos
- **shifts**: quantos deslocamentos de elementos na memória
- **probes**: quantas tentativas para encontrar posição livre
- **node_visits**: quantos nós da árvore foram visitados
- **rotations**: quantas rotações para balancear árvore
- **mem_moves**: total de movimentações de dados na memória

Métricas específicas para tabelas hash:
- **hash_collisions**: quantas colisões de hash ocorreram
- **hash_bucket_len_after**: tamanho da lista após inserção (encadeamento)
- **hash_cluster_len**: tamanho do agrupamento percorrido
- **hash_displacement**: distância da posição ideal até posição final
- **load_factor**: fator de carga da tabela (N/M), calculado dinamicamente

