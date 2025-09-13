# 📊 Experimento de Análise de Estruturas de Dados

## Objetivo do Experimento

Este experimento foi desenvolvido para realizar uma análise comparativa abrangente de diferentes estruturas de dados, medindo sua performance em operações fundamentais (inserção, busca e remoç📊 Configuração do experimento:
  - 12 estruturas diferentes
  - 1 AVL Tree
  - 9 Hash Tables: 3 tamanhos (M=50,100,150) × 3 funções hash (poly31,fnv1a,djb2)
  - 2 Array Linked Lists (ordenada e não-ordenada)
  - [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
  - 5 rounds por configuração
  - Total: 600 execuções

🔧 ESTRUTURA 1/12: AVL Treeavés de múltiplas métricas quantitativas.

## Metodologia Experimental

### Estruturas de Dados Analisadas

O experimento analisa **12 estruturas de dados diferentes**:

1. **AVL Tree** (`AVLTreeDS`)
   - Árvore binária balanceada automaticamente
   - Garante altura logarítmica para todas as operações

2. **Hash Table M=50 poly31** (`HashTableDS(M=50, hash_fn='poly31')`)
   - Função hash polinomial com base 31
   - Tabela pequena para análise de colisões
   - Usa encadeamento separado (chaining) para resolução de colisões

3. **Hash Table M=100 poly31** (`HashTableDS(M=100, hash_fn='poly31')`)
   - Função hash polinomial com base 31
   - Tamanho médio para comparação
   - Usa encadeamento separado (chaining) para resolução de colisões

4. **Hash Table M=150 poly31** (`HashTableDS(M=150, hash_fn='poly31')`)
   - Função hash polinomial com base 31
   - Tabela grande para reduzir colisões
   - Usa encadeamento separado (chaining) para resolução de colisões

5. **Hash Table M=50 fnv1a** (`HashTableDS(M=50, hash_fn='fnv1a')`)
   - Função hash FNV-1a (Fowler–Noll–Vo)
   - Tabela pequena com hash otimizado
   - Usa encadeamento separado (chaining) para resolução de colisões

6. **Hash Table M=100 fnv1a** (`HashTableDS(M=100, hash_fn='fnv1a')`)
   - Função hash FNV-1a (Fowler–Noll–Vo)
   - Tamanho médio para comparação
   - Usa encadeamento separado (chaining) para resolução de colisões

7. **Hash Table M=150 fnv1a** (`HashTableDS(M=150, hash_fn='fnv1a')`)
   - Função hash FNV-1a (Fowler–Noll–Vo)
   - Tabela grande para análise de performance
   - Usa encadeamento separado (chaining) para resolução de colisões

8. **Hash Table M=50 djb2** (`HashTableDS(M=50, hash_fn='djb2')`)
   - Função hash DJB2 de Dan J. Bernstein
   - Tabela pequena com hash amplamente usado
   - Usa encadeamento separado (chaining) para resolução de colisões

9. **Hash Table M=100 djb2** (`HashTableDS(M=100, hash_fn='djb2')`)
   - Função hash DJB2 de Dan J. Bernstein
   - Tamanho médio para comparação
   - Usa encadeamento separado (chaining) para resolução de colisões

10. **Hash Table M=150 djb2** (`HashTableDS(M=150, hash_fn='djb2')`)
    - Função hash DJB2 de Dan J. Bernstein
    - Tabela grande para análise de performance
    - Usa encadeamento separado (chaining) para resolução de colisões

11. **Array Linked List Não-Ordenada** (`ArrayLinkedList()`)
    - Lista ligada implementada com arrays
    - Inserção sempre no final, busca sequencial

12. **Array Linked List Ordenada** (`ArrayLinkedList(sorted_insert=True)`)
    - Lista ligada com inserção ordenada
    - Busca mais eficiente, inserção mais custosa

**Importante**: Todas as Hash Tables usam **encadeamento separado (chaining)** para resolução de colisões. Cada posição da tabela hash contém uma lista ligada que pode armazenar múltiplos elementos quando ocorrem colisões.

### 📏 Parâmetros do Experimento

- **Tamanhos testados**: 1.000, 2.000, 3.000, ..., 10.000 elementos
- **Rounds por configuração**: 5 execuções independentes
- **Total de execuções**: 600 (12 estruturas × 10 tamanhos × 5 rounds)
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
- **`hash_bucket_len_after`**: Tamanho da lista após inserção (encadeamento)
- **`probes`**: Tentativas de acesso aos buckets
- **`load_factor`**: Fator de carga (N/M) da tabela hash

## 🎮 Processo de Execução

### 1️⃣ Fase de Preparação
```python
# Inicialização das estruturas com configurações do experimento
    estruturas = [
        ("AVL Tree", lambda: AVLTreeDS()),
        ("Hash Table M=50 poly31", lambda: HashTableDS(M=50, hash_fn='poly31')),
        ("Hash Table M=100 poly31", lambda: HashTableDS(M=100, hash_fn='poly31')),
        ("Hash Table M=150 poly31", lambda: HashTableDS(M=150, hash_fn='poly31')),
        ("Hash Table M=50 fnv1a", lambda: HashTableDS(M=50, hash_fn='fnv1a')),
        ("Hash Table M=100 fnv1a", lambda: HashTableDS(M=100, hash_fn='fnv1a')),
        ("Hash Table M=150 fnv1a", lambda: HashTableDS(M=150, hash_fn='fnv1a')),
        ("Hash Table M=50 djb2", lambda: HashTableDS(M=50, hash_fn='djb2')),
        ("Hash Table M=100 djb2", lambda: HashTableDS(M=100, hash_fn='djb2')),
        ("Hash Table M=150 djb2", lambda: HashTableDS(M=150, hash_fn='djb2')),
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

O experimento produz **gráficos individuais por métrica**, facilitando a comparação direta entre estruturas:

### 📊 Gráficos Principais (Todas as Estruturas)

**1. Comparações** - Operações: Inserção + Busca + Remoção
- Compara o número total de comparações realizadas por cada estrutura
- Revela a eficiência algorítmica das diferentes implementações

**2. Visitas de Nós** - Operações: Inserção + Busca + Remoção  
- Mede quantos elementos/nós foram acessados durante as operações
- Importante para análise de complexidade espacial

**3. Tempo de Execução (ms)** - Operações: Inserção + Busca + Remoção
- Tempo total de parede medido durante a execução
- Métrica prática para performance real

**4. Movimentações de Memória** - Operações: Inserção + Busca + Remoção
- Conta movimentações e realocações de dados na memória
- Impacto direto na performance do sistema

**5. Tempo de CPU (ms)** - Operações: Inserção + Busca + Remoção
- Tempo de processamento efetivo da CPU
- Exclui tempo de espera do sistema

### 🔍 Gráficos de Análise Específica

**6. Comparações - Inserções**
- Foca exclusivamente na eficiência de inserção
- Revela diferenças na construção das estruturas

**7. Comparações - Buscas**
- Analisa apenas operações de busca
- Crucial para aplicações com muitas consultas

### ⚡ Gráficos Específicos - Hash Tables

Gerados apenas para as **9 variações de Hash Tables** do experimento:

**8. Colisões de Hash**
- Número total de colisões detectadas
- Compara eficácia entre diferentes funções hash (poly31, fnv1a, djb2)
- Mostra impacto do tamanho da tabela (M=50, M=100, M=150)

**9. Tamanho dos Buckets após Inserção**
- Comprimento das listas ligadas em cada bucket após inserções
- Evidencia como diferentes funções hash afetam a distribuição nos buckets

**10. Tentativas de Acesso aos Buckets**
- Número de acessos aos buckets necessários para operações
- Métrica direta de eficiência do encadeamento separado com diferentes funções hash

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
2. **Hash Tables - Efeito da Função Hash**: Diferentes funções hash (poly31, fnv1a, djb2) devem mostrar variação na distribuição e colisões
3. **Hash Tables - Efeito do Tamanho**: Tabelas maiores devem ter menos colisões e melhor performance
4. **Função Hash poly31**: Performance balanceada para strings, boa distribuição geral
5. **Função Hash fnv1a**: Excelente distribuição, baixas colisões, otimizada para velocidade
6. **Função Hash djb2**: Performance rápida, amplamente testada, boa para strings curtas
7. **Array Linked Lists**: Performance linear, com versão ordenada superior em buscas mas inferior em inserções

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
📊 Gerando gráficos individuais por métrica...
  1. Comparações...
  2. Visitas de Nós...
  3. Tempo de Execução (ms)...
  4. Movimentações de Memória...
  5. Tempo de CPU (ms)...
📊 Gerando gráficos específicos por operação...
  6. Comparações em Inserções...
  7. Comparações em Buscas...
📊 Gerando gráficos específicos para Hash Tables...
  8. Colisões de Hash...
  9. Comprimento de Clusters...
  10. Tentativas de Sondagem...

🎉 EXPERIMENTO CONCLUÍDO COM SUCESSO!
📈 Gráficos gerados: 10 (um por métrica)
📁 Verifique a pasta './graficos' para ver todos os arquivos gerados
```

## 📁 Arquivos Gerados

- **Gráficos**: `./graficos/` - Visualizações individuais em PNG de alta resolução (um por métrica)
- **Dados**: Estruturas mantêm histórico completo de todas as execuções
- **Logs**: Output detalhado do processo de execução

## 🎯 Conclusões Esperadas

Este experimento fornece uma base sólida para:

1. **Seleção de estruturas** adequadas para diferentes cenários
2. **Otimização de performance** baseada em métricas reais
3. **Compreensão dos trade-offs** entre diferentes implementações
4. **Validação empírica** de complexidades teóricas
5. **Análise do impacto das funções hash** na performance e distribuição com encadeamento separado
6. **Comparação entre diferentes funções hash** com encadeamento separado

### 📊 Insights Esperados por Métrica

**Gráficos Principais (Todas as Estruturas):**
- **Comparações**: AVL Tree deve mostrar crescimento logarítmico; Hash Tables eficientes com tabelas grandes
- **Visitas de Nós**: Array Lists mostrarão crescimento linear; AVL Tree logarítmico
- **Tempo de Execução**: Hash Tables grandes devem superar outras estruturas em operações mistas
- **Movimentações de Memória**: Array Lists terão mais movimentações em inserções ordenadas
- **Tempo de CPU**: Correlação direta com complexidade algorítmica de cada estrutura

**Análises Específicas:**
- **Inserções**: Array Lists não-ordenadas mais rápidas; ordenadas mais custosas
- **Buscas**: AVL Tree e Hash Tables superiores; Array Lists lineares

**Hash Tables Específicas:**
- **Colisões**: Tabelas maiores (M=150) com menos colisões que pequenas (M=50)
- **Efeito da Função Hash**: fnv1a deve ter menos colisões; poly31 performance equilibrada; djb2 rapidez
- **Buckets**: Encadeamento separado mostra listas ligadas; diferentes funções hash afetam distribuição
- **Acessos**: Eficiência de acesso aos buckets varia com diferentes funções hash
- **Comparação entre Funções Hash**: Trade-offs entre velocidade, distribuição e qualidade do hash com encadeamento separado
- **Array Linked Lists**: Demonstração clara da diferença entre inserção ordenada vs. não-ordenada

---

*Experimento desenvolvido como parte do estudo comparativo de estruturas de dados, implementando framework completo de instrumentação e análise visual com foco na comparação de funções hash usando encadeamento separado (chaining).*

