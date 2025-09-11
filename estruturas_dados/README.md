# 📊 Experimento de Análise de Estruturas de Dados

## Objetivo do Experimento

Este experimento foi desenvolvido para realizar uma análise comparativa abrangente de diferentes estruturas de dados, medindo sua performance em operações fundamentais (inserção, busca e remoção) através de múltiplas métricas quantitativas.

## Metodologia Experimental

### Estruturas de Dados Analisadas

O experimento analisa **9 estruturas de dados diferentes**:

1. **AVL Tree** (`AVLTreeDS`)
   - Árvore binária balanceada automaticamente
   - Garante altura logarítmica para todas as operações

2. **Hash Table com Sondagem Quadrática M=50** (`HashTableDS(M=50, probing='quadratic')`)
   - Resolução de colisões por sondagem quadrática
   - Tabela pequena para análise de colisões

3. **Hash Table com Sondagem Quadrática M=100** (`HashTableDS(M=100, probing='quadratic')`)
   - Resolução de colisões por sondagem quadrática
   - Tamanho médio para comparação

4. **Hash Table com Sondagem Quadrática M=1000** (`HashTableDS(M=1000, probing='quadratic')`)
   - Resolução de colisões por sondagem quadrática
   - Tabela grande para reduzir colisões

5. **Hash Table com Sondagem Linear M=50** (`HashTableDS(M=50, probing='linear')`)
   - Resolução de colisões por sondagem linear
   - Tabela pequena para estudar clustering primário

6. **Hash Table com Sondagem Linear M=100** (`HashTableDS(M=100, probing='linear')`)
   - Resolução de colisões por sondagem linear
   - Tamanho médio para comparação

7. **Hash Table com Sondagem Linear M=1000** (`HashTableDS(M=1000, probing='linear')`)
   - Resolução de colisões por sondagem linear
   - Tabela grande para análise de performance

8. **Array Linked List Não-Ordenada** (`ArrayLinkedList()`)
   - Lista ligada implementada com arrays
   - Inserção sempre no final, busca sequencial

9. **Array Linked List Ordenada** (`ArrayLinkedList(sorted_insert=True)`)
   - Lista ligada com inserção ordenada
   - Busca mais eficiente, inserção mais custosa

### 📏 Parâmetros do Experimento

- **Tamanhos testados**: 1.000, 2.000, 3.000, ..., 10.000 elementos
- **Rounds por configuração**: 5 execuções independentes
- **Total de execuções**: 450 (9 estruturas × 10 tamanhos × 5 rounds)
- **Operações testadas**: Inserção, Busca e Remoção

### 📊 Métricas Coletadas

Cada estrutura é instrumentada para coletar as seguintes métricas:

#### 🔍 Métricas de Eficiência Algorítmica
- **`comparisons`**: Número total de comparações realizadas
- **`node_visits`**: Quantidade de nós/elementos visitados
- **`probes`**: Tentativas de acesso (específico para hash tables)

#### ⏱️ Métricas de Tempo
- **`wall_time_ms`**: Tempo total de execução (milissegundos)
- **`proc_time_ms`**: Tempo de processamento da CPU (milissegundos)

#### 💾 Métricas de Memória
- **`mem_moves`**: Movimentações de dados na memória
- **`mem_accesses`**: Total de acessos à memória

#### 🔧 Métricas Específicas para Hash Tables
- **`hash_collisions`**: Número de colisões detectadas
- **`hash_cluster_len`**: Comprimento médio dos clusters
- **`hash_bucket_len_after`**: Tamanho do bucket após inserção (encadeamento)
- **`hash_displacement`**: Distância da posição ideal até posição final
- **`load_factor`**: Fator de carga (N/M) da tabela hash

## 🎮 Processo de Execução

### 1️⃣ Fase de Preparação
```python
# Inicialização das estruturas com configurações do experimento
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
```

### 2️⃣ Fase de Execução
Para cada combinação de (estrutura, tamanho, round):

1. **Geração de dados**: Criação de dataset aleatório único
2. **Operações sequenciais**:
   - Inserção de todos os elementos
   - Busca por elementos existentes e inexistentes
   - Remoção de elementos selecionados
3. **Coleta de métricas**: Registro automático via framework `OpRecord`

### 3️⃣ Fase de Análise
```python
# Agregação estatística dos dados coletados
df_summary = BaseDataStructure.rounds_summary_df(
    structures=lista_estruturas,
    metrics=['comparisons', 'node_visits', 'wall_time_ms'],
    agg='sum',
    op_filter=('insert', 'search', 'remove')
)
```

## 📈 Visualizações Geradas

O experimento produz **5 tipos de gráficos comparativos**:

### 1️⃣ Gráfico de Eficiência Geral
- **Métricas**: Comparações, Visitas de Nós, Tempo Total
- **Operações**: Inserção + Busca + Remoção
- **Objetivo**: Visão geral da performance

### 2️⃣ Gráfico de Sistema (CPU e Memória)
- **Métricas**: Movimentações de Memória, Tempo de CPU
- **Operações**: Inserção + Busca + Remoção
- **Objetivo**: Análise de recursos do sistema

### 3️⃣ Análise Específica - Inserções
- **Métricas**: Comparações, Visitas, Movimentações
- **Operações**: Apenas Inserção
- **Objetivo**: Performance de construção da estrutura

### 4️⃣ Análise Específica - Buscas
- **Métricas**: Comparações, Visitas, Tempo
- **Operações**: Apenas Busca
- **Objetivo**: Eficiência de consultas

### 5️⃣ Métricas Específicas - Hash Tables
- **Métricas**: Colisões, Clusters, Probes
- **Operações**: Inserção + Busca
- **Objetivo**: Análise detalhada de hash tables

## 🔧 Implementação Técnica

### Framework de Instrumentação
```python
class BaseDataStructure:
    def __init__(self, name: str, **params: Any):
        self.op_record = OpRecord()
        self.counters = Counters()
    
    @classmethod
    def rounds_summary_df(cls, structures, metrics=None, agg='sum', op_filter=('insert',)):
        """Gera DataFrame agregado com estatísticas entre rounds de múltiplas estruturas"""
        # Implementação completa de agregação entre estruturas
```

### Sistema de Métricas
```python
class OpRecord:
    # Métricas de tempo e sistema
    wall_time_ms: float = 0       # Tempo total de execução (milissegundos)
    proc_time_ms: float = 0       # Tempo de processamento da CPU (milissegundos)
    cpu_user_ms: float = 0        # Tempo gasto executando código do programa
    cpu_system_ms: float = 0      # Tempo gasto em operações do sistema
    rss_mb: float = 0             # Quantidade de memória RAM ocupada (MB)
    tracemalloc_peak_kb: float = 0 # Pico de memória alocada pelo Python (KB)
    
    # Métricas de eficiência algorítmica
    comparisons: int = 0          # Comparações realizadas
    node_visits: int = 0          # Nós/elementos visitados
    probes: int = 0              # Tentativas de acesso
    swaps: int = 0               # Trocas de posição entre elementos
    shifts: int = 0              # Deslocamentos de elementos na memória
    rotations: int = 0           # Rotações para balancear árvore
    mem_moves: int = 0           # Total de movimentações de dados na memória
    
    # Métricas específicas para hash tables
    hash_collisions: int = 0      # Colisões de hash detectadas
    hash_bucket_len_after: int = 0 # Tamanho do bucket após inserção
    hash_cluster_len: int = 0     # Comprimento do cluster percorrido
    hash_displacement: int = 0    # Distância da posição ideal
```

### Geração de Gráficos
```python
class GraficosMetricas:
    def plotar_metricas_estruturas(self, structures, metrics, agg='sum'):
        """Gera gráficos comparativos usando matplotlib/seaborn"""
        # Configuração automática de layout
        # Suporte a múltiplas métricas simultaneamente
        # Exportação em alta resolução
```

## 📋 Resultados Esperados

### Hipóteses a Serem Testadas

1. **AVL Tree**: Deve apresentar performance logarítmica consistente para todas as operações
2. **Hash Tables com Sondagem Quadrática**: Menor clustering que sondagem linear, performance melhor com tabelas maiores
3. **Hash Tables com Sondagem Linear**: Mais clustering, mas acesso sequencial pode ser cache-friendly
4. **Efeito do Tamanho da Tabela (M)**: Tabelas maiores devem ter menos colisões e melhor performance
5. **Array Linked Lists**: Performance linear, com versão ordenada superior em buscas mas inferior em inserções

### Métricas de Interesse

- **Escalabilidade**: Como as métricas crescem com o tamanho
- **Consistência**: Variação entre diferentes rounds
- **Trade-offs**: Relação entre diferentes métricas (tempo vs. memória)

## 🚀 Execução do Experimento

Para executar o experimento completo:

```bash
cd trab01
python rodar_experimento.py
```

### Saída Esperada
```
� INICIANDO EXPERIMENTO COMPLETO DE ESTRUTURAS DE DADOS
============================================================
Arquivos removidos da pasta de gráficos: 0
� Configuração do experimento:
  - 9 estruturas diferentes
  - [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
  - 5 rounds por configuração
  - Total: 450 execuções

🔧 ESTRUTURA 1/9: AVL Tree
  📏 N = 1,000 elementos
    🔄 Round 1/5 [0.2%]
    🔄 Round 2/5 [0.4%]
    ...
    
📈 GERANDO GRÁFICOS COMPARATIVOS...
📊 1. Métricas gerais de eficiência...
📊 2. Métricas de sistema (CPU e memória)...
📊 3. Análise específica - Inserções...
📊 4. Análise específica - Buscas...
📊 5. Métricas específicas - Hash Tables...

🎉 EXPERIMENTO CONCLUÍDO COM SUCESSO!
📈 Gráficos gerados: 5
📁 Verifique a pasta './graficos' para ver todos os arquivos gerados
```

## 📁 Arquivos Gerados

- **Gráficos**: `./graficos/` - Visualizações em PNG de alta resolução
- **Dados**: Estruturas mantêm histórico completo de todas as execuções
- **Logs**: Output detalhado do processo de execução

## 🎯 Conclusões Esperadas

Este experimento fornece uma base sólida para:

1. **Seleção de estruturas** adequadas para diferentes cenários
2. **Otimização de performance** baseada em métricas reais
3. **Compreensão dos trade-offs** entre diferentes implementações
4. **Validação empírica** de complexidades teóricas
5. **Análise do impacto do tamanho da tabela** hash na performance
6. **Comparação entre sondagem linear e quadrática** em diferentes contextos

### 📊 Insights Esperados

- **AVL Tree**: Performance logarítmica consistente, ideal para operações balanceadas
- **Hash Tables Pequenas (M=50)**: Mais colisões, demonstração clara dos efeitos de clustering
- **Hash Tables Grandes (M=1000)**: Menos colisões, performance próxima ao ideal O(1)
- **Sondagem Linear vs Quadrática**: Trade-off entre simplicidade e redução de clustering
- **Array Linked Lists**: Demonstração clara da diferença entre inserção ordenada vs. não-ordenada

---

*Experimento desenvolvido como parte do estudo comparativo de estruturas de dados, implementando framework completo de instrumentação e análise visual.*

