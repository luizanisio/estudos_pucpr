import sys
import os
from typing import List, Optional, Iterable, Tuple, Literal

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    from util_estrutura import BaseDataStructure
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)

class GraficosMetricas:
    """
    Permite escolher entre escala linear, logarítmica ou automática para cada métrica.
    """
    
    def __init__(self, pasta_graficos: str = "./graficos") -> None:
        """Inicializa a classe criando diretório de saída se necessário."""
        self.pasta_graficos = pasta_graficos
        os.makedirs(pasta_graficos, exist_ok=True)
    
    def plotar_metricas(
        self,
        structures: List[BaseDataStructure],
        metrics: Optional[Iterable[str]] = None,
        agg: str = "sum",
        op_filter: Tuple[str, ...] = ("insert",),
        escala: Literal["linear", "log", "auto"] = "linear",
        limite_auto: float = 100.0,
        titulo_personalizado: Optional[str] = None,
        largura: int = 16,
        altura: int = 8,
        mostrar_comparacao: bool = False,
        gravar_csv = True
    ) -> str:
        """
        Gera gráficos com controle explícito sobre a escala utilizada.
        
        Args:
            structures: Lista de estruturas que já coletaram métricas
            metrics: Lista de métricas a plotar
            agg: Como agregar dentro da rodada ("sum" ou "mean")
            op_filter: Operações a considerar
            escala: "linear", "log" ou "auto" para decidir automaticamente
            limite_auto: Limite de variação para escala automática (padrão: 100x)
            titulo_personalizado: Título customizado
            largura: Largura do gráfico
            altura: Altura do gráfico
            mostrar_comparacao: Se True, gera lado a lado linear vs log
            gravar_csv: exporta um csv com os dados do gráfico
            
        Returns:
            str: Caminho do arquivo gerado
        """
        try:
            if not structures:
                raise ValueError("Lista de estruturas não pode estar vazia")
            
            # Obtém DataFrame
            df = BaseDataStructure.rounds_summary_df(
                structures=structures,
                metrics=metrics,
                agg=agg,
                op_filter=op_filter
            )
            
            if df.empty:
                raise ValueError("Nenhum dado encontrado para plotar.")
            
            # Se mostrar_comparacao = True, gera lado a lado
            if mostrar_comparacao:
                return self._plotar_comparacao_escalas(
                    df, agg, op_filter, titulo_personalizado, largura, altura
                )
            
            # Gera nome do arquivo
            nome_arquivo = self._gerar_nome_arquivo_avancado(
                structures, list(df['metric'].unique()), agg, op_filter, escala
            )
            
            if gravar_csv:
                caminho_csv = f"{self.pasta_graficos}/{nome_arquivo}.csv"
                df.to_csv(caminho_csv, index=False)
                print(f"📄 Dados exportados para CSV: {caminho_csv}")
            
            # Configuração do matplotlib
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Obtém métricas
            metricas_unicas = df['metric'].unique()
            n_metricas = len(metricas_unicas)
            
            # Layout dos subplots
            if n_metricas == 1:
                fig, ax = plt.subplots(1, 1, figsize=(largura, altura))
                axes = [ax]
            else:
                cols = min(2, n_metricas)
                rows = (n_metricas + cols - 1) // cols
                fig, axes_raw = plt.subplots(rows, cols, figsize=(largura * cols, altura * rows))
                
                # Converte para lista
                if rows == 1 and cols == 1:
                    axes = [axes_raw]
                elif rows == 1 or cols == 1:
                    axes = list(np.atleast_1d(axes_raw))
                else:
                    axes = []
                    for i in range(rows):
                        for j in range(cols):
                            axes.append(axes_raw[i, j])
            
            # Plota cada métrica
            for i, metrica in enumerate(metricas_unicas):
                ax = axes[i] if n_metricas > 1 else axes[0]
                
                # Filtra dados para esta métrica
                df_metrica = df[df['metric'] == metrica].copy()
                
                # Plota linha para cada estrutura
                for ds_name in df_metrica['ds_name'].unique():
                    df_ds = df_metrica[df_metrica['ds_name'] == ds_name].copy()
                    df_ds = df_ds.sort_values('instances')
                    
                    x_values = np.array(df_ds['instances'].values)
                    y_values = np.array(df_ds['mean_per_round'].values)
                    std_values = np.array(df_ds['std_per_round'].values)
                    
                    # Plota linha principal
                    ax.plot(
                        x_values, y_values,
                        marker='o', linewidth=2, markersize=6,
                        label=ds_name, alpha=0.8
                    )
                    
                    # Barras de erro se há variabilidade
                    if any(std_values > 0):
                        ax.errorbar(
                            x_values, y_values, yerr=std_values,
                            fmt='none', alpha=0.3, capsize=3
                        )
                
                # Decide escala para esta métrica
                escala_usada = self._decidir_escala(df_metrica, escala, limite_auto)
                
                # Configuração do subplot
                ax.set_xlabel('N (Número de Elementos)', fontsize=12)
                
                if escala_usada == "log":
                    ax.set_yscale('log')
                    ax.set_ylabel(f'{metrica} ({agg}) - ESCALA LOG', fontsize=12)
                    ax.set_title(f'{metrica} - Escala Logarítmica', fontsize=14, fontweight='bold')
                else:
                    ax.set_ylabel(f'{metrica} ({agg})', fontsize=12)
                    ax.set_title(f'{metrica} - Escala Linear', fontsize=14, fontweight='bold')
                
                ax.grid(True, alpha=0.3)
                ax.legend(frameon=True, fancybox=True, shadow=True)
            
            # Remove subplots extras
            if n_metricas > 1:
                for j in range(n_metricas, len(axes)):
                    fig.delaxes(axes[j])
            
            # Título geral
            if titulo_personalizado:
                titulo = titulo_personalizado
            else:
                ops_str = "+".join(op_filter)
                escala_info = escala if escala != "auto" else f"auto (limite: {limite_auto}x)"
                titulo = f'Comparação de Métricas - Escala: {escala_info}\n({agg} por operação: {ops_str})'
            
            fig.suptitle(titulo, fontsize=16, fontweight='bold', y=0.98)
            
            # Ajusta layout e salva
            plt.tight_layout()
            plt.subplots_adjust(top=0.93)
            
            caminho_grafico = f"{self.pasta_graficos}/{nome_arquivo}.png"
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"📈 Gráfico avançado salvo: {caminho_grafico}")
            return caminho_grafico
            
        except Exception as e:
            print(f"❌ Erro ao gerar gráfico avançado: {e}")
            raise
    
    def _decidir_escala(self, df_metrica, escala_config, limite_auto):
        """Decide qual escala usar para uma métrica específica."""
        if escala_config in ["linear", "log"]:
            return escala_config
        
        # Escala automática
        y_min = df_metrica['mean_per_round'].min()
        y_max = df_metrica['mean_per_round'].max()
        
        if y_min <= 0:
            return "linear"  # Log não funciona com zeros/negativos
        
        variacao = y_max / y_min
        return "log" if variacao > limite_auto else "linear"
    
    def _plotar_comparacao_escalas(self, df, agg, op_filter, titulo_personalizado, largura, altura):
        """Gera gráfico lado a lado com escala linear vs logarítmica."""
        nome_arquivo = f"comparacao_escalas_{agg}_{'_'.join(op_filter)}"
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Para cada métrica, cria comparação lado a lado
        metricas = df['metric'].unique()
        
        for metrica in metricas:
            df_metrica = df[df['metric'] == metrica].copy()
            
            # Calcula variação
            y_min = df_metrica['mean_per_round'].min()
            y_max = df_metrica['mean_per_round'].max()
            variacao = y_max / max(y_min, 1e-10)
            
            # Cria subplot lado a lado
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(largura, altura))
            
            # Plota em ambas as escalas
            for ds_name in df_metrica['ds_name'].unique():
                df_ds = df_metrica[df_metrica['ds_name'] == ds_name].copy()
                df_ds = df_ds.sort_values('instances')
                
                x_values = np.array(df_ds['instances'].values)
                y_values = np.array(df_ds['mean_per_round'].values)
                std_values = np.array(df_ds['std_per_round'].values)
                
                # Escala linear
                ax1.plot(x_values, y_values, marker='o', linewidth=2, 
                        markersize=6, label=ds_name, alpha=0.8)
                if any(std_values > 0):
                    ax1.errorbar(x_values, y_values, yerr=std_values, 
                               fmt='none', alpha=0.3, capsize=3)
                
                # Escala logarítmica  
                ax2.plot(x_values, y_values, marker='o', linewidth=2, 
                        markersize=6, label=ds_name, alpha=0.8)
                if any(std_values > 0):
                    ax2.errorbar(x_values, y_values, yerr=std_values, 
                               fmt='none', alpha=0.3, capsize=3)
            
            # Configuração escala linear
            ax1.set_xlabel('N (Número de Elementos)', fontsize=12)
            ax1.set_ylabel(f'{metrica} ({agg})', fontsize=12)
            ax1.set_title(f'ESCALA LINEAR\n{metrica}', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Configuração escala logarítmica
            ax2.set_xlabel('N (Número de Elementos)', fontsize=12)
            ax2.set_ylabel(f'{metrica} ({agg}) - LOG', fontsize=12)
            ax2.set_title(f'ESCALA LOGARÍTMICA\n{metrica}', fontsize=14, fontweight='bold')
            ax2.set_yscale('log')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Título geral
            titulo = titulo_personalizado or f'Comparação de Escalas - {metrica}'
            fig.suptitle(f'{titulo}\nVariação: {variacao:.1f}x', 
                        fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            # Salva gráfico
            nome_metrica = metrica.replace('_', '')
            caminho = f"{self.pasta_graficos}/{nome_arquivo}_{nome_metrica}.png"
            plt.savefig(caminho, dpi=300, bbox_inches='tight')
            print(f"📊 Comparação de escalas salva: {caminho}")
            plt.close()
        
        return f"{self.pasta_graficos}/{nome_arquivo}_*.png"
    
    def _gerar_nome_arquivo_avancado(self, structures, metrics, agg, op_filter, escala):
        """Gera nome de arquivo incluindo informação da escala."""
        # Nomes das estruturas
        ds_names = [s.__class__.__name__ for s in structures]
        if len(ds_names) <= 3:
            ds_str = "_".join(ds_names)
        else:
            ds_str = f"{len(ds_names)}estruturas"
        
        # Métricas
        if len(metrics) <= 3:
            metrics_str = "_".join(m.replace("_", "") for m in metrics)
        else:
            metrics_str = f"{len(metrics)}metricas"
        
        # Operações
        ops_str = "_".join(op_filter)
        
        # Nome final
        nome = f"{ds_str}_{metrics_str}_{agg}_{ops_str}_{escala}"
        nome = nome.replace(" ", "_").replace("/", "_").replace("\\", "_")
        nome = nome[:120]  # Limita tamanho
        
        return nome

    @classmethod
    def limpar_pasta_graficos(cls, pasta = './graficos'):
        """Limpa a pasta de gráficos antes de gerar novos."""
        import os
        import shutil

        # lista os arquivos csv e png da pasta e remove
        q = 0
        if os.path.isdir(pasta):
            for filename in os.listdir(pasta):
                if filename.endswith('.csv') or filename.endswith('.png'):
                    file_path = os.path.join(pasta, filename)
                    os.remove(file_path)
                    q += 1
        print(f"GraficosMetricas: Arquivos removidos da pasta {pasta}: {q}")
        os.makedirs(pasta, exist_ok=True)


def teste_classe():
    """Testa a classe avançada com diferentes configurações de escala."""
    print("🧪 TESTANDO CLASSE GRAFICOS AVANÇADA")
    print("=" * 50)
    
    from util_estrutura import ArrayLinkedList, AVLTreeDS, HashTableDS
    
    # Cria estruturas de teste
    structures = [
        ArrayLinkedList(),
        AVLTreeDS(),
        HashTableDS(M=30)
    ]
    
    # Gera dados de teste
    for structure in structures:
        structure.clear_log()
        for N in [10, 50, 100]:
            structure.carregar_dados(N)
            # Algumas buscas
            for i in range(min(N, 5)):
                matricula = f"{i:06d}"
                structure.search(matricula)
    
    # Inicializa classe avançada
    graficos = GraficosMetricas()
    graficos.limpar_pasta_graficos()
    
    # Teste 1: Escala linear forçada
    print("\n📊 Teste 1: Escala Linear Forçada")
    caminho1 = graficos.plotar_metricas(
        structures=structures,
        metrics=['comparisons', 'node_visits'],
        escala="linear",
        titulo_personalizado="Teste - Escala Linear Forçada"
    )
    
    # Teste 2: Escala logarítmica forçada  
    print("\n📊 Teste 2: Escala Logarítmica Forçada")
    caminho2 = graficos.plotar_metricas(
        structures=structures,
        metrics=['comparisons', 'node_visits'],
        escala="log",
        titulo_personalizado="Teste - Escala Logarítmica Forçada"
    )
    
    # Teste 3: Escala automática
    print("\n📊 Teste 3: Escala Automática")
    caminho3 = graficos.plotar_metricas(
        structures=structures,
        metrics=['comparisons', 'node_visits'],
        escala="auto",
        limite_auto=50.0,
        titulo_personalizado="Teste - Escala Automática (limite: 50x)"
    )
    
    # Teste 4: Comparação lado a lado
    print("\n📊 Teste 4: Comparação Lado a Lado")
    caminho4 = graficos.plotar_metricas(
        structures=structures,
        metrics=['comparisons'],
        mostrar_comparacao=True,
        titulo_personalizado="Teste - Comparação Linear vs Log"
    )
    
    print("\n✅ TESTES CONCLUÍDOS!")
    print("📁 Gráficos salvos na pasta: ./graficos/")


if __name__ == "__main__":
    teste_classe()
