# util_estrutura.py
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, List, Tuple, Callable, Iterable
from collections import defaultdict
import time
import tracemalloc
import json
import csv
import random
import uuid
from util_dados import get_dados
random.seed(42)

try:
    import psutil  # para métricas de sistema
    _HAS_PSUTIL = True
except Exception:
    _HAS_PSUTIL = False
    raise ImportError('ATENÇÃO: psutil não disponível ... pip install psutil')

# -----------------------------
# Contadores genéricos por operação
# -----------------------------
@dataclass
class Counters:
    # operações básicas comuns a todas as estruturas
    comparisons: int = 0       # quantas vezes duas chaves foram comparadas
    swaps: int = 0             # quantas trocas de posição entre elementos
    shifts: int = 0            # quantos deslocamentos de elementos na memória
    probes: int = 0            # quantas tentativas para encontrar posição livre
    node_visits: int = 0       # quantos nós da árvore foram visitados
    rotations: int = 0         # quantas rotações para balancear árvore

    # métricas específicas para tabelas hash
    hash_collisions: int = 0           # quantas colisões de hash ocorreram
    hash_bucket_len_after: int = 0     # tamanho da lista após inserção (encadeamento)
    hash_cluster_len: int = 0          # tamanho do agrupamento percorrido
    hash_displacement: int = 0         # distância da posição ideal até posição final

    def reset(self) -> None:
        # comuns
        self.comparisons = 0
        self.swaps = 0
        self.shifts = 0
        self.probes = 0
        self.node_visits = 0
        self.rotations = 0
        # hash
        self.hash_collisions = 0
        self.hash_bucket_len_after = 0
        self.hash_cluster_len = 0
        self.hash_displacement = 0

    @property
    def mem_moves(self) -> int:
        # aproximação: swap ≈ 2 writes; shift ≈ 1 write
        return self.swaps * 2 + self.shifts


# -----------------------------
# Registro estruturado de cada chamada (para plotar depois)
# -----------------------------
@dataclass
class OpRecord:
    ds_name: str
    params: Dict[str, Any]
    op: str                   # 'insert' | 'remove' | 'search'
    key: Any                  # chave (matrícula)
    success: bool
    wall_time_ms: float       # tempo total decorrido durante a operação
    proc_time_ms: float       # tempo de processamento usado pela CPU
    cpu_user_ms: Optional[float]    # tempo gasto executando código do programa
    cpu_system_ms: Optional[float]  # tempo gasto em operações do sistema
    rss_mb: Optional[float]         # quantidade de memória RAM ocupada (MB)
    tracemalloc_peak_kb: float      # pico de memória alocada pelo Python (KB)

    # contadores de operações básicas
    comparisons: int          # quantas vezes duas chaves foram comparadas
    swaps: int               # quantas trocas de posição entre elementos
    shifts: int              # quantos deslocamentos de elementos na memória
    probes: int              # quantas tentativas para encontrar posição livre
    node_visits: int         # quantos nós da árvore foram visitados
    rotations: int           # quantas rotações para balancear árvore
    mem_moves: int           # total de movimentações de dados na memória

    # métricas específicas para tabelas hash
    hash_collisions: int = 0        # quantas colisões de hash ocorreram
    hash_bucket_len_after: int = 0  # tamanho da lista após inserção (encadeamento)
    hash_cluster_len: int = 0       # tamanho do agrupamento percorrido
    hash_displacement: int = 0      # distância da posição ideal até posição final

    # espaço extra opcional para futuras métricas customizadas
    extras: Dict[str, Any] = field(default_factory=dict)
    
    # identificador do round experimental
    round_id: Optional[str] = None  # identificador único do round de experimento

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # flatten params para conveniência (ex.: "param_M=..." em CSV)
        for k, v in self.params.items():
            d[f"param_{k}"] = v
        # flatten extras (prefixo x_)
        if self.extras:
            for k, v in self.extras.items():
                d[f"x_{k}"] = v
        return d


# -----------------------------
# Base: define interface e instrumentação
# -----------------------------
class BaseDataStructure:
    """
    Classe base para arrays, BST e hash table do Trabalho 01.

    Subclasses devem implementar:
        - _insert_impl(key, value) -> bool
        - _remove_impl(key) -> bool
        - _search_impl(key) -> Optional[Dict[str, Any]]

    Observação:
    - Chave: matrícula (string zero-padded).
    - Valor: dicionário com os dados completos.
    """

    def __init__(self, name: str, **params: Any) -> None:
        self.name = name
        self.params = params
        self.counters = Counters()
        self._log: List[OpRecord] = []
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self._proc = psutil.Process() if _HAS_PSUTIL else None
        self._extras_current_op: Dict[str, Any] = {}
        self._metricas_ignorar = set()
        self._current_round_id = str(uuid.uuid4())  # gera ID único automaticamente

    # --------- Interface pública ---------
    def insert(self, key: str, value: Dict[str, Any]) -> bool:
        return self._instrument("insert", key, lambda: self._insert_impl(key, value))

    def remove(self, key: str) -> bool:
        return self._instrument("remove", key, lambda: self._remove_impl(key))

    def search(self, key: str) -> Optional[Dict[str, Any]]:
        result_ref: Dict[str, Any] = {"_ptr": None}
        def _do():
            result_ref["_ptr"] = self._search_impl(key)
            return result_ref["_ptr"] is not None
        self._instrument("search", key, _do)
        return result_ref["_ptr"]

    # --------- Hooks obrigatórios nas subclasses ---------
    def _insert_impl(self, key: str, value: Dict[str, Any]) -> bool:  # pragma: no cover
        raise NotImplementedError
    def _remove_impl(self, key: str) -> bool:  # pragma: no cover
        raise NotImplementedError
    def _search_impl(self, key: str) -> Optional[Dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError

    # --------- Utilidades para subclasses (com contagem) ---------
    def cmp_keys(self, a: str, b: str) -> int:
        """Compara chaves e atualiza contador de comparações."""
        self.counters.comparisons += 1
        return (a > b) - (a < b)

    def note_swap(self, times: int = 1) -> None:
        self.counters.swaps += times
    def note_shift(self, times: int = 1) -> None:
        self.counters.shifts += times
    def note_probe(self, times: int = 1) -> None:
        self.counters.probes += times
    def note_visit(self, times: int = 1) -> None:
        self.counters.node_visits += times
    def note_rotation(self, times: int = 1) -> None:
        self.counters.rotations += times

    # --------- Utilidades específicas para HASH ---------
    def note_hash_collision(self, times: int = 1) -> None:
        """Incrementa o nº de colisões desta operação."""
        self.counters.hash_collisions += times

    def set_hash_bucket_len_after(self, length: int) -> None:
        """Define o tamanho do bucket após o insert (encadeamento)."""
        if length >= 0:
            self.counters.hash_bucket_len_after = int(length)

    def set_hash_cluster_len(self, length: int) -> None:
        """Define o comprimento de cluster/sondagem percorrido (open addressing)."""
        if length >= 0:
            self.counters.hash_cluster_len = int(length)

    def set_hash_displacement(self, distance: int) -> None:
        """Define a distância do índice-base à posição final (open addressing)."""
        if distance >= 0:
            self.counters.hash_displacement = int(distance)

    def note_extra(self, key: str, value: Any) -> None:
        """Armazena par (k,v) extra para o OpRecord atual (será flatten como x_<k>)."""
        self._extras_current_op[key] = value

    # --------- Instrumentação ---------
    def _instrument(self, op: str, key: Any, fn) -> bool:
        self.counters.reset()
        self._extras_current_op = {}

        # tempos
        t0_wall = time.perf_counter_ns()
        t0_proc = time.process_time_ns()

        # CPU/mem (psutil)
        if self._proc is not None:
            cpu0 = self._proc.cpu_times()
            rss0 = self._proc.memory_info().rss
            cpu_user0, cpu_sys0 = cpu0.user, cpu0.system
        else:
            cpu_user0 = cpu_sys0 = None
            rss0 = None

        # tracemalloc
        _, _ = tracemalloc.get_traced_memory()

        # executa
        success = fn()

        # tempos
        t1_proc = time.process_time_ns()
        t1_wall = time.perf_counter_ns()

        # CPU/mem (psutil)
        if self._proc is not None:
            cpu1 = self._proc.cpu_times()
            rss1 = self._proc.memory_info().rss
            cpu_user1, cpu_sys1 = cpu1.user, cpu1.system
            cpu_user_ms = (cpu_user1 - cpu_user0) * 1000.0
            cpu_sys_ms = (cpu_sys1 - cpu_sys0) * 1000.0
            rss_mb = (rss1 / (1024 ** 2)) if rss1 is not None else None
        else:
            cpu_user_ms = cpu_sys_ms = None
            rss_mb = None

        _, peak1 = tracemalloc.get_traced_memory()
        peak_kb = peak1 / 1024.0

        rec = OpRecord(
            ds_name=self.name,
            params=self.params,
            op=op,
            key=key,
            success=bool(success),
            wall_time_ms=(t1_wall - t0_wall) / 1e6,
            proc_time_ms=(t1_proc - t0_proc) / 1e6,
            cpu_user_ms=cpu_user_ms,
            cpu_system_ms=cpu_sys_ms,
            rss_mb=rss_mb,
            tracemalloc_peak_kb=peak_kb,
            round_id=self._current_round_id,

            # comuns
            comparisons=self.counters.comparisons,
            swaps=self.counters.swaps,
            shifts=self.counters.shifts,
            probes=self.counters.probes,
            node_visits=self.counters.node_visits,
            rotations=self.counters.rotations,
            mem_moves=self.counters.mem_moves,

            # hash (por operação)
            hash_collisions=self.counters.hash_collisions,
            hash_bucket_len_after=self.counters.hash_bucket_len_after,
            hash_cluster_len=self.counters.hash_cluster_len,
            hash_displacement=self.counters.hash_displacement,

            # extras
            extras=self._extras_current_op.copy(),
        )
        self._log.append(rec)
        return bool(success)

    # --------- Relato das métricas ---------
    @property
    def log(self) -> List[OpRecord]:
        return self._log
    
    @property
    def round_id(self) -> str:
        return self._current_round_id

    def clear_log(self) -> None:
        self._log.clear()

    def export_jsonl(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for rec in self._log:
                f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")

    def export_csv(self, path: str) -> None:
        if not self._log:
            with open(path, "w", newline="", encoding="utf-8") as f:
                pass
            return
        rows = [rec.to_dict() for rec in self._log]
        fieldnames = sorted(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    def export_metrics_json(self) -> Dict[str, Any]:
        """
        Exporta as métricas da estrutura em formato JSON compatível com rounds_summary_df.
        
        Retorna um dicionário contendo:
        - ds_name: nome da estrutura
        - params: parâmetros da estrutura
        - round_id: identificador do round atual
        - metrics: lista com todas as métricas dos OpRecord do log
        
        Returns:
            Dict[str, Any]: Dicionário com dados da estrutura e lista de métricas
        """
        metrics = []
        for rec in self._log:
            metric_dict = rec.to_dict()
            metrics.append(metric_dict)
            metrics_out = list(self._metricas_ignorar)
        
        return {
            "ds_name": self.name,
            "params": self.params.copy(),
            "round_id": self._current_round_id,
            "metrics": metrics,
            "metrics_out": metrics_out
        }

    def summary(self, agg: str = "sum") -> Dict[str, Dict[str, float]]:
        """
        Retorna um resumo por operação (médias/somas) para gráficos.
        Inclui métricas comuns e de hash.
        { 'insert': { 'wall_time_ms': ..., 'hash_collisions': ..., ...}, 'search': {...}, ... }
        """
        from collections import defaultdict
        agg_sum = defaultdict(lambda: defaultdict(float))
        agg_cnt = defaultdict(int)

        agg = agg.lower().strip()
        if agg not in ("mean", "sum"):
            raise ValueError("agg deve ser 'mean' ou 'sum'.")

        # métricas conhecidas (inclui hash específicas)
        metrics = (
            "wall_time_ms", "proc_time_ms",
            "cpu_user_ms", "cpu_system_ms",
            "rss_mb", "tracemalloc_peak_kb",
            "comparisons", "swaps", "shifts", "probes",
            "node_visits", "rotations", "mem_moves",
            "hash_collisions", "hash_bucket_len_after",
            "hash_cluster_len", "hash_displacement",
        )

        # agrega
        for rec in self._log:
            agg_cnt[rec.op] += 1
            d = rec.to_dict()
            for m in metrics:
                v = d.get(m)
                if v is not None:
                    try:
                        agg_sum[rec.op][m] += float(v)
                    except Exception:
                        pass
            # também agrega extras numéricos (prefixo x_)
            for k, v in d.items():
                if k.startswith("x_"):
                    try:
                        val = float(v)
                    except Exception:
                        continue
                    agg_sum[rec.op][k] += val

        out: Dict[str, Dict[str, float]] = {}
        if agg == 'sum':
            # somas
            out = agg_sum
        else:
            # médias
            for op, cnt in agg_cnt.items():
                out[op] = {}
                for m, s in agg_sum[op].items():
                    out[op][m] = s / cnt if cnt else 0.0
        return out

    ##################################################
    ## métodos para lote e métricas

    def carregar_dados(self, qtd=1000, sorted = False):
        ''' sorted só para o caso do método existir
        '''
        dados = get_dados(qtd)
        self.__dados_lote  = dados
        for linha in dados:
            if sorted and 'insert_sorted' in self.params:
                  self.params['insert_sorted'](key = linha['Matricula'], value = linha)
            else:
               self.insert(key = linha['Matricula'], value = linha)

    def remover_dados(self, qtd=100):
        dados = random.sample(self.__dados_lote, qtd)
        for linha in dados:
            self.remove(key = linha['Matricula'])

    def buscar_dados(self, qtd=100):
        dados = random.sample(self.__dados_lote, qtd)
        for linha in dados:
            self.search(key = linha['Matricula'])

    def descarregar_dados(self):
        ''' limpa os dados carregados para liberar memória
            - útil quando os dados forem usados só para preparar as
              métricas para gerar gráficos e não são mais necessários
              para operações na estrutura
        '''
        self.__dados_lote = None

    def print_summary(self, agg: str = "sum"):
        print('>---------------------------------------<')
        if agg.strip().lower() == 'sum':
           print('Soma por operação:')
        else:
           print('Médias por operação:')
        for c,v in self.summary().items():
            if isinstance(v, dict):
                for k, vv in v.items():
                    if k not in self._metricas_ignorar:
                       print(f'  - {c}.{k}: {vv}')
            else:
                print(f'  - {c}: {v}')

        print('\n','- ' * 30)

    @classmethod
    def rounds_summary_df(
        cls,
        metrics_data: List[Dict[str, Any]],
        metrics: Optional[Iterable[str]] = None,
        agg: str = "sum",
        op_filter: Tuple[str, ...] = ("insert",),
    ):
        """
        Gera um DataFrame com uma linha por (ds_name, N, metric),
        contendo média ENTRE RODADAS, nº de rodadas e desvio-padrão ENTRE RODADAS.

        Colunas:
          - ds_name         : str (nome da estrutura)
          - instances       : int (N da rodada = nº de inserts no bloco)
          - metric          : str (nome da métrica)
          - mean_per_round  : float (média entre rodadas para esse N)
          - rounds          : int (quantidade de rodadas para esse N)
          - std_per_round   : float (desvio-padrão entre rodadas para esse N; 0 se rounds==1)

        Parâmetros:
          - metrics_data : lista de dicionários com dados das estruturas e suas métricas
                          (formato retornado por export_metrics_json)
          - metrics  : lista de métricas a considerar; se None usa um conjunto padrão
          - agg      : como agregar dentro da rodada ("sum" ou "mean")
          - op_filter: quais operações entram dentro da rodada (default: só 'insert')
        """
        try:
            import numpy as np
            import pandas as pd
        except Exception as e:
            raise RuntimeError(
                "Este método requer numpy e pandas instalados."
            ) from e

        if agg not in ("sum", "mean"):
            raise ValueError("agg deve ser 'sum' ou 'mean'.")

        # Métricas padrão conhecidas (mesmas do summary) + 'load_factor' opcional
        default_metrics = (
            "wall_time_ms", "proc_time_ms",
            "cpu_user_ms", "cpu_system_ms",
            "rss_mb", "tracemalloc_peak_kb",
            "comparisons", "swaps", "shifts", "probes",
            "node_visits", "rotations", "mem_moves",
            "hash_collisions", "hash_bucket_len_after",
            "hash_cluster_len", "hash_displacement",
            # especial (não existe no OpRecord; calculada via N/M):
            "load_factor",
        )
        metrics = tuple(metrics) if metrics is not None else default_metrics

        def _extract_cycles_from_data(data_item: Dict[str, Any]):
            """
            Agrupa os registros por round_id para identificar inequivocamente cada round.
            Retorna cycles baseados em round_id único.
            """
            metrics_records = data_item.get("metrics", [])
            if not metrics_records:
                return []

            # Agrupa por round_id
            rounds_dict = defaultdict(list)
            for rec_dict in metrics_records:
                round_id = rec_dict.get("round_id") or "unknown"
                rounds_dict[round_id].append(rec_dict)

            cycles = []
            for round_id, records in rounds_dict.items():
                if not records:
                    continue
                
                # Conta inserções no round para determinar N
                insert_count = sum(1 for r in records if r.get("op") == "insert")
                
                # Cria o cycle com todas as operações do round
                cycle = {
                    "round_id": round_id,
                    "insert_attempts": insert_count,
                    "records": records,
                    "ds_name": data_item.get("ds_name"),
                    "params": data_item.get("params", {}),
                }
                cycles.append(cycle)
            
            return cycles

        def _aggregate_over_records(recs, metric: str, params: Dict[str, Any], N_cycle: int) -> Optional[float]:
            """Agrega a métrica dentro da rodada (entre os OpRecord filtrados)."""
            if metric == "load_factor":
                M = params.get("M")
                if M:
                    try:
                        return N_cycle / float(M)
                    except Exception:
                        return None
                return None

            vals = []
            for r in recs:
                v = r.get(metric)
                if v is None:
                    continue
                try:
                    vals.append(float(v))
                except Exception:
                    pass
            if not vals:
                return None
            return sum(vals) if agg == "sum" else (sum(vals) / len(vals))

        # Acumulador de valores por (ds_name, N, metric) ao longo das rodadas
        by_key = defaultdict(list)  # key => list[valor_da_rodada]

        for data_item in metrics_data:
            if not isinstance(data_item, dict):
                continue
            cycles = _extract_cycles_from_data(data_item)
            for cyc in cycles:
                N = cyc["insert_attempts"]
                round_id = cyc["round_id"]
                ds_name = cyc["ds_name"]
                params = cyc["params"]
                
                # Filtra registros das operações desejadas dentro da rodada
                recs = [r for r in cyc["records"] if r.get("op") in op_filter]
                if not recs:
                    continue

                for metric in metrics:
                    val = _aggregate_over_records(recs, metric, params, N)
                    if val is None:
                        continue
                    key = (ds_name, int(N), metric)
                    by_key[key].append(float(val))

        # Constrói o DataFrame final
        rows = []
        for (ds_name, N, metric), values in by_key.items():
            if not values:
                continue
            rounds = len(values)
            mean_val = round(float(np.mean(values)), 5)
            
            # Cálculo seguro do desvio padrão
            if rounds > 1:
                std_val = round(float(np.std(values, ddof=1)), 5)
            else:
                std_val = 0.0
                
            rows.append({
                "ds_name": ds_name,
                "instances": int(N),
                "metric": metric,
                "mean_per_round": mean_val,
                "rounds": rounds,
                "std_per_round": std_val,
                "values": values,  # para debug/inspeção
            })

        if not rows:
            # DataFrame vazio, mas com colunas esperadas
            return pd.DataFrame(columns=[
                "ds_name", "instances", "metric",
                "mean_per_round", "rounds", "std_per_round"
            ])

        df = pd.DataFrame(rows)
        df.sort_values(by=["ds_name", "metric", "instances"], inplace=True, kind="stable")
        df.reset_index(drop=True, inplace=True)
        return df
    
#############################################################################################    
#############################################################################################    
#############################################################################################    
class ArrayLinkedList(BaseDataStructure):
    """
    Lista simplesmente encadeada (LinkedList) para o Trabalho 1,
    implementada com integração à BaseDataStructure.

    - Chave: matrícula (str, 6 dígitos)
    - Valor: dicionário do funcionário

    Inserção: O(1) inserção direta (fim da lista) ou O(n) inserção ordenada
    Busca: O(n) linear como esperado para lista ligada
    Remoção: O(n) linear para localizar + O(1) para remover
    Memória: Crescimento linear adequado com número de elementos

    Parâmetros do construtor:
      - default_pos: int
          -1  -> inserir no fim (tail) [padrão]
           0  -> inserir no início (head)
           k  -> inserir na posição k (0 <= k <= length)
      - sorted_insert: bool
          True -> insere mantendo ordem crescente de chave; ignora default_pos
    """

    class _Node:
        __slots__ = ("key", "value", "next")
        def __init__(self, key: str, value: Dict[str, Any]):
            self.key = key
            self.value = value
            self.next: Optional["ArrayLinkedList._Node"] = None

    def __init__(self, default_pos: int = -1, sorted_insert: bool = False, **params: Any) -> None:
        nome = f'ArrayLinkedList(def={default_pos}|{"sorted" if sorted_insert else "unsorted"})'
        super().__init__(nome, default_pos=default_pos, sorted_insert=sorted_insert, **params)
        self.head: Optional[ArrayLinkedList._Node] = None
        self.tail: Optional[ArrayLinkedList._Node] = None
        self.length: int = 0

        self.default_pos = int(default_pos)
        self.sorted_insert = bool(sorted_insert)
        self._metricas_ignorar =  {'rotations', 'hash_collisions', 'hash_bucket_len_after', 'hash_cluster_len', 'hash_displacement'}

    # =========================
    # Implementações Base
    # =========================
    def _insert_impl(self, key: str, value: Dict[str, Any]) -> bool:
        new_node = self._Node(key, value)

        # 2) lista vazia → caso base
        if self.head is None:
            self.head = self.tail = new_node
            self.length = 1
            # writes: head, tail
            self.note_shift(2)
            return True

        # 3) inserção ordenada (se habilitada)
        if self.sorted_insert:
            return self._insert_sorted(new_node)

        # 4) inserção por posição
        pos = self.default_pos
        if pos == -1:
            # fim (tail)
            assert self.tail is not None
            self.tail.next = new_node
            self.note_shift(1)      # tail.next = new_node
            self.tail = new_node
            self.note_shift(1)      # tail = new_node
            self.length += 1
            return True

        if pos == 0:
            # início (head)
            new_node.next = self.head
            self.note_shift(1)      # new_node.next = head
            self.head = new_node
            self.note_shift(1)      # head = new_node
            self.length += 1
            return True

        # inserir em posição intermediária: 0 < pos <= length
        if 0 <= pos <= self.length:
            prev = self._node_at(pos - 1)
            if prev is None:
                return False
            new_node.next = prev.next
            self.note_shift(1)      # new_node.next = prev.next
            prev.next = new_node
            self.note_shift(1)      # prev.next = new_node
            # atualiza tail se inseriu no final (pos == length)
            if prev is self.tail:
                self.tail = new_node
                self.note_shift(1)  # tail = new_node
            self.length += 1
            return True

        # posição inválida - não insere
        return False

    def _remove_impl(self, key: str) -> bool:
        if self.head is None:
            return False

        # remover head
        self.note_visit(1)
        if self.cmp_keys(self.head.key, key) == 0:
            old_head = self.head
            self.head = self.head.next
            self.note_shift(1)          # head = head.next
            if self.head is None:
                # lista ficou vazia; zera tail
                self.tail = None
                self.note_shift(1)      # tail = None
            del old_head
            self.length -= 1
            return True

        # remover no meio/fim
        prev = self.head
        cur = self.head.next
        while cur is not None:
            self.note_visit(1)
            if self.cmp_keys(cur.key, key) == 0:
                # religa: prev -> cur.next
                prev.next = cur.next
                self.note_shift(1)      # prev.next = cur.next
                if cur is self.tail:
                    self.tail = prev
                    self.note_shift(1)  # tail = prev
                del cur
                self.length -= 1
                return True
            prev = cur
            cur = cur.next

        return False

    def _search_impl(self, key: str) -> Optional[Dict[str, Any]]:
        node = self._find_node(key)
        return node.value if node else None

    # =========================
    # Helpers internos
    # =========================
    def _find_node(self, key: str) -> Optional[_Node]:
        """Busca linear; conta visitas e comparações."""
        cur = self.head
        while cur is not None:
            self.note_visit(1)
            if self.cmp_keys(cur.key, key) == 0:
                return cur
            cur = cur.next
        return None

    def _node_at(self, index: int) -> Optional[_Node]:
        """Retorna nó na posição index (0-based)."""
        if index < 0 or index >= self.length:
            return None
        cur = self.head
        i = 0
        while cur is not None and i < index:
            self.note_visit(1)
            cur = cur.next
            i += 1
        # conta visita do nó final encontrado
        if cur is not None:
            self.note_visit(1)
        return cur

    def _insert_sorted(self, new_node: _Node) -> bool:
        """Insere mantendo ordem crescente de chave (lexicográfica)."""
        # inserir no início?
        if self.cmp_keys(new_node.key, self.head.key) < 0:
            new_node.next = self.head
            self.note_shift(1)      # new_node.next = head
            self.head = new_node
            self.note_shift(1)      # head = new_node
            self.length += 1
            return True

        # encontrar posição (prev < new <= cur)
        prev = self.head
        cur = self.head.next
        while cur is not None and self.cmp_keys(cur.key, new_node.key) < 0:
            self.note_visit(1)
            prev = cur
            cur = cur.next

        new_node.next = prev.next
        self.note_shift(1)          # new_node.next = prev.next
        prev.next = new_node
        self.note_shift(1)          # prev.next = new_node
        if prev is self.tail:
            self.tail = new_node
            self.note_shift(1)      # tail = new_node
        self.length += 1
        return True

    # =========================
    # Utilidades opcionais
    # =========================
    def to_list(self) -> list[tuple[str, Dict[str, Any]]]:
        """Exporta como lista [(key, value), ...] (útil p/ depuração)."""
        out = []
        cur = self.head
        while cur is not None:
            out.append((cur.key, cur.value))
            cur = cur.next
        return out

##########################################################################################    
##########################################################################################    
##########################################################################################    
class AVLTreeDS(BaseDataStructure):
    """
    AVL Tree/BST para o Trabalho 1, herdando da BaseDataStructure.
    - Chave: matrícula (str, zero-padded)
    - Valor: dicionário com dados do funcionário

    Parâmetros:
    - balanced: bool (default=True)
        True -> comporta-se como AVL Tree com rotações para balanceamento
        False -> comporta-se como BST simples sem rotações

    Métricas:
    - comparisons: via cmp_keys
    - node_visits: cada vez que acessamos/avaliamos um nó
    - rotations: em rotações LL, RR, LR, RL (apenas quando balanced=True)
    """
    
    class _Node:
        __slots__ = ("key", "value", "left", "right", "height")
        def __init__(self, key: str, value: Dict[str, Any]):
            self.key = key
            self.value = value
            self.left: Optional["AVLTreeDS._Node"] = None
            self.right: Optional["AVLTreeDS._Node"] = None
            self.height: int = 1  # altura do nó (AVL)

    def __init__(self, balanced: bool = True, **params: Any) -> None:
        name = f"AVLTree({'balanced' if balanced else 'unbalanced'})"
        super().__init__(name, balanced=balanced, **params)
        self.root: Optional[AVLTreeDS._Node] = None
        self.balanced = balanced
        self._metricas_ignorar = {
            'hash_collisions', 'hash_bucket_len_after', 
            'hash_cluster_len', 'hash_displacement'
        }

    # ----------------------------
    # Implementações exigidas pela Base
    # ----------------------------
    def _insert_impl(self, key: str, value: Dict[str, Any]) -> bool:
        self.root, inserted = self._insert(self.root, key, value)
        return inserted

    def _remove_impl(self, key: str) -> bool:
        self.root, removed = self._remove(self.root, key)
        return removed

    def _search_impl(self, key: str) -> Optional[Dict[str, Any]]:
        cur = self.root
        while cur is not None:
            self.note_visit(1)
            c = self.cmp_keys(key, cur.key)
            if c == 0:
                return cur.value
            elif c < 0:
                cur = cur.left
            else:
                cur = cur.right
        return None

    # ----------------------------
    # Helpers AVL
    # ----------------------------
    def _height(self, n: Optional[AVLTreeDS._Node]) -> int:
        return n.height if n is not None else 0

    def _update_height(self, n: AVLTreeDS._Node) -> None:
        n.height = 1 + max(self._height(n.left), self._height(n.right))

    def _balance_factor(self, n: Optional[AVLTreeDS._Node]) -> int:
        if n is None:
            return 0
        return self._height(n.left) - self._height(n.right)

    def _rotate_right(self, z: AVLTreeDS._Node) -> AVLTreeDS._Node:
        self.note_rotation(1)  # conta rotação
        y = z.left
        assert y is not None
        T2 = y.right

        y.right = z
        z.left = T2

        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_left(self, z: AVLTreeDS._Node) -> AVLTreeDS._Node:
        self.note_rotation(1)  # conta rotação
        y = z.right
        assert y is not None
        T2 = y.left

        y.left = z
        z.right = T2

        self._update_height(z)
        self._update_height(y)
        return y

    def _rebalance(self, node: AVLTreeDS._Node) -> AVLTreeDS._Node:
        # NOVO: contamos a avaliação do nó no rebalance
        self.note_visit(1)

        self._update_height(node)
        
        # Se balanceamento está desabilitado, apenas retorna o nó sem rotações
        if not self.balanced:
            return node
            
        bf = self._balance_factor(node)

        # LL
        if bf > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)

        # LR
        if bf > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # RR
        if bf < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)

        # RL
        if bf < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    # ----------------------------
    # Insert (recursivo)
    # ----------------------------
    def _insert(self, node: Optional[AVLTreeDS._Node], key: str, value: Dict[str, Any]) -> tuple[Optional[AVLTreeDS._Node], bool]:
        if node is None:
            self.note_visit(1)
            return AVLTreeDS._Node(key, value), True

        self.note_visit(1)
        c = self.cmp_keys(key, node.key)
        if c < 0:
            node.left, inserted = self._insert(node.left, key, value)
        else:
            node.right, inserted = self._insert(node.right, key, value)

        node = self._rebalance(node)
        return node, True

    # ----------------------------
    # Remove (recursivo)
    # ----------------------------
    def _remove(self, node: Optional[AVLTreeDS._Node], key: str) -> tuple[Optional[AVLTreeDS._Node], bool]:
        if node is None:
            return None, False

        self.note_visit(1)
        c = self.cmp_keys(key, node.key)
        if c < 0:
            node.left, removed = self._remove(node.left, key)
        elif c > 0:
            node.right, removed = self._remove(node.right, key)
        else:
            # nó alvo
            removed = True
            # 0 ou 1 filho
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # 2 filhos: substitui pelo sucessor (mínimo da direita)
            succ = self._min_node(node.right)
            # CONTAGEM DE ESCRITAS LÓGICAS (para mem_moves):
            self.note_shift(2)  # key e value
            node.key, node.value = succ.key, succ.value
            # remove o sucessor
            node.right, _ = self._remove(node.right, succ.key)

        if not removed or node is None:
            return node, removed

        node = self._rebalance(node)
        return node, True

    def _min_node(self, node: AVLTreeDS._Node) -> AVLTreeDS._Node:
        cur = node
        self.note_visit(1)
        while cur.left is not None:
            cur = cur.left
            self.note_visit(1)
        return cur

    # ----------------------------
    # Percursos (utilitários)
    # ----------------------------
    def inorder_items(self):
        yield from self._inorder(self.root)

    def _inorder(self, node: Optional[AVLTreeDS._Node]):
        if node is None:
            return
        yield from self._inorder(node.left)
        yield (node.key, node.value)
        yield from self._inorder(node.right)
    
##########################################################################################    
##########################################################################################    
##########################################################################################    

class HashTableDS(BaseDataStructure):
    """
    Tabela Hash para o Trabalho 1, herdando de BaseDataStructure.
    Usa encadeamento separado (chaining) para resolução de colisões.

    Parâmetros:
      - M: tamanho da tabela (ex.: 100, 1000, 5000)
      - hash_fn: "poly31" | "fnv1a" | "djb2"
    """

    # ---------------------------
    # Construtor
    # ---------------------------
    def __init__(
        self,
        M: int = 1000,
        hash_fn: str = "poly31",
        **params: Any,
    ) -> None:
        nome = f"HashTable({M}|chaining|{hash_fn})"
        super().__init__(nome, M=M, hash_fn=hash_fn, **params)

        assert M > 0, "M deve ser > 0"
        self.M = int(M)

        # Seleção da função hash
        self._hash1 = self._get_hash(hash_fn)

        # Estrutura interna: array de listas para encadeamento separado
        self._table: List[List[Tuple[str, Dict[str, Any]]]] = [[] for _ in range(self.M)]
        self._max_chain_len = 0

        # Métricas agregadas
        self._n_items = 0
        self._collisions_total = 0  # soma de colisões ao longo das inserções

        self._metricas_ignorar = {
            'rotations', 'hash_cluster_len', 'hash_displacement', 'node_visits'
        }

    # ---------------------------
    # Hashes disponíveis
    # ---------------------------
    def _get_hash(self, name: str) -> Callable[[str], int]:
        name = (name or "").lower()
        if name == "poly31":
            return self._hash_poly31
        if name == "fnv1a":
            return self._hash_fnv1a
        if name == "djb2":
            return self._hash_djb2
        raise ValueError("hash_fn deve ser 'poly31' | 'fnv1a' | 'djb2'")

    @staticmethod
    def _hash_poly31(s: str) -> int:
        p, m = 31, 1_000_000_007
        h, p_pow = 0, 1
        for ch in s:
            h = (h + (1 + ord(ch)) * p_pow) % m
            p_pow = (p_pow * p) % m
        return h

    @staticmethod
    def _hash_fnv1a(s: str) -> int:
        h = 0xcbf29ce484222325
        fnv_prime = 0x100000001b3
        for ch in s:
            h ^= ord(ch)
            h = (h * fnv_prime) & 0xffffffffffffffff
        return h

    @staticmethod
    def _hash_djb2(s: str) -> int:
        h = 5381
        for ch in s:
            h = ((h << 5) + h) + ord(ch)  # h*33 + c
            h &= 0xffffffffffffffff
        return h

    def _idx1(self, key: str) -> int:
        return self._hash1(key) % self.M

    # ---------------------------
    # Implementações exigidas pela Base
    # ---------------------------
    def _insert_impl(self, key: str, value: Dict[str, Any]) -> bool:
        return self._insert_chain(key, value)

    def _remove_impl(self, key: str) -> bool:
        return self._remove_chain(key)

    def _search_impl(self, key: str) -> Optional[Dict[str, Any]]:
        return self._search_chain(key)

    # ---------------------------
    # Encadeamento separado
    # ---------------------------
    def _insert_chain(self, key: str, value: Dict[str, Any]) -> bool:
        i = self._idx1(key)
        self.note_probe(1)  # acesso ao bucket
        bucket = self._table[i]

        # Colisão nesta operação: bucket já possuía elementos
        if len(bucket) > 0:
            self._collisions_total += 1
            self.note_hash_collision(1)

        # Inserção
        bucket.append((key, value))
        self._n_items += 1

        # Tamanho do bucket após o insert
        self.set_hash_bucket_len_after(len(bucket))

        if len(bucket) > self._max_chain_len:
            self._max_chain_len = len(bucket)
        return True

    def _remove_chain(self, key: str) -> bool:
        i = self._idx1(key)
        self.note_probe(1)
        bucket = self._table[i]
        for idx, (k, _) in enumerate(bucket):
            self.cmp_keys(k, key)
            if k == key:
                self.note_shift(1)  # 1 write lógico
                bucket.pop(idx)
                self._n_items -= 1
                return True
        return False

    def _search_chain(self, key: str) -> Optional[Dict[str, Any]]:
        i = self._idx1(key)
        self.note_probe(1)
        bucket = self._table[i]
        for k, v in bucket:
            self.cmp_keys(k, key)
            if k == key:
                return v
        return None

    # ---------------------------
    # Métricas agregadas
    # ---------------------------
    @property
    def collisions_total(self) -> int:
        return self._collisions_total

    @property
    def n_items(self) -> int:
        return self._n_items

    def load_factor(self) -> float:
        return self._n_items / float(self.M)

    def max_chain_length(self) -> int:
        return self._max_chain_len
    
    
    
##########################################################################################    
##########################################################################################    
##########################################################################################    


if __name__ == '__main__':
    # Teste básico das funcionalidades
    ds = ArrayLinkedList(default_pos=0)
    ds.carregar_dados(1000)
    ds.print_summary('sum')
    ds.remover_dados(100)
    ds.print_summary('sum')
    ds.buscar_dados(100)
    ds.print_summary('sum')