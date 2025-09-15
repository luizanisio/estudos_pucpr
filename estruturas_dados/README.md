# 📊 Experimento de Análise de Estruturas de Dados

## Objetivo do Experimento

Este experimento foi desenvolvido para realizar uma análise comparativa abrangente de diferentes estruturas de dados, medindo sua performance em operações fundamentais (inserção, busca e remoção) através de múltiplas métricas quantitativas.

## Metodologia Experimental

### Estruturas de Dados Analisadas

O experimento analisa **estruturas de dados diferentes** baseadas nas configurações do script `rodar_experimento.py`:

1. **AVL Tree Balanceada** (`AVLTreeDS(balanced=True)`)
   - Árvore binária balanceada automaticamente
   - Garante altura logarítmica para todas as operações

2. **AVL Tree Não Balanceada** (`AVLTreeDS(balanced=False)`)
   - Árvore binária sem auto-balanceamento (vira BST)
   - Permite análise comparativa do impacto do balanceamento

3. **Hash Tables** (variando M e função hash)
   - Tamanhos de tabela definidos pela variável `M_HASH_TABLE` 
   - Três funções hash: poly31, fnv1a, djb2
   - Usa encadeamento separado (chaining) para resolução de colisões
   - Total: `len(M_HASH_TABLE) × 3` configurações

4. **Array Linked List Não-Ordenada** (`ArrayLinkedList(sorted_insert=False)`)
   - Lista ligada implementada com arrays
   - Inserção sempre no final, busca sequencial

5. **Array Linked List Ordenada** (`ArrayLinkedList(sorted_insert=True)`)
   - Lista ligada com inserção ordenada
   - Busca mais eficiente, inserção mais custosa

### Configurações Específicas das Hash Tables

As Hash Tables são testadas com todas as combinações de:
- **Tamanhos (M)**: Valores definidos na variável `M_HASH_TABLE`
- **Funções Hash**: 
  - `poly31`: Função hash polinomial com base 31
  - `fnv1a`: Função hash FNV-1a (Fowler–Noll–Vo) 
  - `djb2`: Função hash DJB2 de Dan J. Bernstein

**Importante**: Todas as Hash Tables usam **encadeamento separado (chaining)** para resolução de colisões. Cada posição da tabela hash contém uma lista ligada que pode armazenar múltiplos elementos quando ocorrem colisões.

### 📏 Parâmetros do Experimento

Os parâmetros são definidos pelas variáveis no script `rodar_experimento.py`:

- **Tamanhos testados**: Valores da variável `TAMANHOS` 
- **Valores M das Hash Tables**: Valores da variável `M_HASH_TABLE`
- **Rounds por configuração**: Valor da variável `N_ROUNDS`
- **Total de estruturas**: 2 AVL Trees + `len(M_HASH_TABLE) × 3` Hash Tables + 2 Array Lists
- **Total de execuções**: `len(estruturas) × len(TAMANHOS) × N_ROUNDS`
- **Operações testadas**: Inserção, Busca e Remoção

### Configuração Atual (valores padrão)
- **`TAMANHOS`**: [1000, 5000, 10000, 50000, 100000] elementos
- **`M_HASH_TABLE`**: [100, 1000, 5000] 
- **`N_ROUNDS`**: 5 execuções independentes

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
    ("AVL Tree balanceada", lambda: AVLTreeDS(balanced=True)),
    ("AVL Tree não balanceada", lambda: AVLTreeDS(balanced=False)),
    ("Array LinkedList Não ordenado", lambda: ArrayLinkedList(sorted_insert=False)),
    ("Array LinkedList Ordenado", lambda: ArrayLinkedList(sorted_insert=True))
]

# Adiciona Hash Tables dinamicamente baseadas na variável M_HASH_TABLE
for h in M_HASH_TABLE:
    estruturas.append((f"Hash Table M={h} poly31", lambda h=h: HashTableDS(M=h, hash_fn='poly31')))
    estruturas.append((f"Hash Table M={h} fnv1a", lambda h=h: HashTableDS(M=h, hash_fn='fnv1a')))
    estruturas.append((f"Hash Table M={h} djb2", lambda h=h: HashTableDS(M=h, hash_fn='djb2')))

# Total de estruturas: 4 + (len(M_HASH_TABLE) × 3)
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

Gerados apenas para as **variações de Hash Tables** do experimento (baseadas em `M_HASH_TABLE`):

**8. Colisões de Hash**
- Número total de colisões detectadas
- Compara eficácia entre diferentes funções hash (poly31, fnv1a, djb2)
- Mostra impacto do tamanho da tabela (valores de `M_HASH_TABLE`)

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
    def plotar_metricas_estruturas(self, metrics_data, metrics, agg='sum'):
        """Gera gráficos comparativos usando matplotlib/seaborn"""
        # Configuração automática de layout
        # Suporte a múltiplas métricas simultaneamente
        # Exportação em alta resolução
```

## 📋 Resultados Esperados

### Hipóteses a Serem Testadas

1. **AVL Tree**: Quando balanceada, deve apresentar performance logarítmica consistente para todas as operações
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

## 📁 Arquivos Gerados

- **Gráficos**: `./graficos/` - Visualizações individuais em PNG de alta resolução (um por métrica)
- **Dados**: Estruturas mantêm histórico completo de todas as execuções
- **Rounds**: `./rounds/` - Métricas geradas por round para continuar a execução do experimento de onde parou
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
- **Colisões**: Tabelas maiores (valores maiores em `M_HASH_TABLE`) com menos colisões
- **Efeito da Função Hash**: fnv1a deve ter menos colisões; poly31 performance equilibrada; djb2 rapidez
- **Buckets**: Encadeamento separado mostra listas ligadas; diferentes funções hash afetam distribuição
- **Acessos**: Eficiência de acesso aos buckets varia com diferentes funções hash
- **Comparação entre Tamanhos M**: Trade-offs entre uso de memória e performance baseados nos valores de `M_HASH_TABLE`
- **Array Linked Lists**: Demonstração clara da diferença entre inserção ordenada vs. não-ordenada

---

*Experimento desenvolvido como parte do estudo comparativo de estruturas de dados, implementando framework completo de instrumentação e análise visual com foco na comparação de funções hash usando encadeamento separado (chaining). Os parâmetros são configuráveis através das variáveis `TAMANHOS`, `M_HASH_TABLE` e `N_ROUNDS` no script `rodar_experimento.py`.*

