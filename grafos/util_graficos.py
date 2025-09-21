"""
Módulo para geração de gráficos comparativos de algoritmos de grafos.

Este módulo contém funcionalidades para criar visualizações dos resultados
de experimentos com algoritmos de busca em grafos, incluindo gráficos de
comparação de métricas como custo, tempo de execução e nós visitados.
"""

import os
import matplotlib.pyplot as plt
from util_grafos import GrafosBase


class GeradorGraficos:
    """ Gera gráficos comparativos de algoritmos de grafos. """
    
    def __init__(self):
        pass
    
    def gerar_graficos_comparativos(self, df, arquivo_grafo, origem, destino, pasta_saida="resultados", mostrar = False):
        """
        Gera gráficos comparativos das métricas coletadas.
        Parâmetros:
            df: DataFrame com os resultados dos algoritmos
            arquivo_grafo: Caminho do arquivo JSON do grafo
            origem: Nó de origem (string)
            destino: Nó de destino (string)
            pasta_saida: Pasta onde salvar os gráficos (padrão: "resultados")
        Retorna:
            str: Caminho do arquivo de imagem gerado ou None se não foi possível gerar
        """
        # Filtra apenas algoritmos que encontraram caminho
        df_sucesso = df[df['encontrou_caminho'] == True].copy()
        
        if df_sucesso.empty:
            print("Nenhum algoritmo encontrou caminho. Não é possível gerar gráficos.")
            return None

        # Obtém o título com rótulos dos nós
        nome_grafo = self._titulo_com_rotulos(arquivo_grafo, origem, destino)

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(nome_grafo, fontsize=14)
        
        # Gera os 4 gráficos principais
        self._grafico_custo_total(axes[0, 0], df_sucesso)
        self._grafico_nos_visitados(axes[0, 1], df_sucesso)
        self._grafico_tempo_execucao(axes[1, 0], df_sucesso)
        self._grafico_tamanho_caminho(axes[1, 1], df_sucesso)
        
        # Ajusta layout e salva
        plt.tight_layout()
        nome_arquivo_grafico = f"{os.path.splitext(os.path.basename(arquivo_grafo))[0]}_{origem}_{destino}_barras.png"
        nome_arquivo_grafico = os.path.join(pasta_saida, nome_arquivo_grafico)
        plt.savefig(nome_arquivo_grafico, dpi=300, bbox_inches='tight')
        print(f"Gráficos salvos em: {nome_arquivo_grafico}")
        if mostrar:
            plt.show()
        
        return nome_arquivo_grafico
        
    def _titulo_com_rotulos(self, arquivo_grafo, origem, destino):
        """ Obtém o título incluindo rótulos dos nós quando disponíveis. """
        try:
            # Carrega o grafo para obter os rótulos dos nós
            grafo_temp = GrafosBase()
            grafo_temp.carregar_json(arquivo_grafo)
            
            # Obtém os rótulos de origem e destino
            label_origem = grafo_temp.get_label(origem)
            label_destino = grafo_temp.get_label(destino)
            
            # Monta o subtítulo com rótulos apenas se forem diferentes das chaves
            subtitulo_origem = (f"{origem} ({label_origem})" 
                              if label_origem and label_origem != origem 
                              else origem)
            subtitulo_destino = (f"{destino} ({label_destino})" 
                               if label_destino and label_destino != destino 
                               else destino)
            
            return f"Comparando algoritmos: {subtitulo_origem} → {subtitulo_destino}"
            
        except Exception as e:
            print(f"Erro ao obter rótulos dos nós: {e}")
            return f"({origem} → {destino})"
    
    def _grafico_custo_total(self, ax, df_sucesso):
        ax.bar(df_sucesso['algoritmo'], df_sucesso['custo_total'], color='skyblue')
        ax.set_title('Custo Total do Caminho')
        ax.set_ylabel('Custo')
        ax.tick_params(axis='x', rotation=45)
    
    def _grafico_nos_visitados(self, ax, df_sucesso):
        ax.bar(df_sucesso['algoritmo'], df_sucesso['num_nos_visitados'], color='lightgreen')
        ax.set_title('Número de Nós Visitados')
        ax.set_ylabel('Nós Visitados')
        ax.tick_params(axis='x', rotation=45)
    
    def _grafico_tempo_execucao(self, ax, df_sucesso):
        ax.bar(df_sucesso['algoritmo'], df_sucesso['tempo_execucao_medio'], 
               yerr=df_sucesso['tempo_desvio_padrao'], color='coral', capsize=5)
        ax.set_title('Tempo de Execução Médio')
        ax.set_ylabel('Tempo (segundos)')
        ax.tick_params(axis='x', rotation=45)
    
    def _grafico_tamanho_caminho(self, ax, df_sucesso):
        ax.bar(df_sucesso['algoritmo'], df_sucesso['num_nos_caminho'], color='gold')
        ax.set_title('Tamanho do Caminho (Número de Nós)')
        ax.set_ylabel('Número de Nós')
        ax.tick_params(axis='x', rotation=45)


def gerar_graficos(df, arquivo_grafo, origem, destino, mostrar = False):
    """ Função de conveniência para manter compatibilidade com código existente. """
    gerador = GeradorGraficos()
    return gerador.gerar_graficos_comparativos(df, arquivo_grafo, origem, destino, mostrar =mostrar)


if __name__ == "__main__":
    print("Módulo util_graficos - Geração de gráficos para algoritmos de grafos")
    print("Use: from util_graficos import gerar_graficos")