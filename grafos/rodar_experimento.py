'''
Experimento que recebe um grafo de um arquivo JSON, executa os algoritmos BFS, DFS, Busca Gananciosa, A* e Dijkstra, coletando
métricas disponíveis (tempo, custo, número de nós visitados, etc) e salvando os resultados em um arquivo CSV.
Também imprime os resultados na tela.
Pode ser usado para comparar desempenho dos algoritmos em diferentes grafos.

Utiliza o pacote util_graficos para gerar gráficos a partir dos dados coletados.
Os arquivos são salvos na pasta "resultados".
'''

import os
import time
import statistics
import pandas as pd
from util_grafos import GrafosDijkstra
from util_grafos_aestrela import GrafoAEstrela
from util_grafos_outros import GrafoBFS, GrafoDFS, GrafoGananciosa
from util_graficos import gerar_graficos

# Configurações do experimento
ORIGEM, DESTINO = 'A', 'J'
ARQUIVO_GRAFO = 'base_grafos/grafo_simples.json'
NUM_EXECUCOES = 5  # Número de execuções para calcular média e desvio padrão

def executar_algoritmo(classe_grafo, nome_algoritmo, arquivo_grafo, origem, destino):
    """Executa um algoritmo específico e coleta suas métricas.
    
    Args:
        classe_grafo: Classe do algoritmo (ex: GrafoBFS)
        nome_algoritmo: Nome do algoritmo para identificação
        arquivo_grafo: Caminho do arquivo JSON do grafo
        origem: Nó de origem
        destino: Nó de destino
        
    Returns:
        dict: Dicionário com as métricas coletadas
    """
    # Instancia o grafo e carrega os dados
    grafo = classe_grafo()
    grafo.carregar_json(arquivo_grafo)
    
    # Mede o tempo de execução
    tempo_inicio = time.time()
    encontrou_caminho = grafo.encontrar_caminho(origem, destino)
    tempo_execucao = time.time() - tempo_inicio
    
    # Coleta as métricas do algoritmo
    if encontrou_caminho:
        estatisticas = grafo.movimentos.get_estatisticas()
        caminho = grafo.movimentos.get_caminho_completo()
        custo_total = grafo.movimentos.get_custo_total()
        
        return {
            'algoritmo': nome_algoritmo,
            'origem': origem,
            'destino': destino,
            'encontrou_caminho': True,
            'caminho': ' -> '.join(caminho),
            'custo_total': custo_total,
            'num_nos_caminho': len(caminho),
            'num_nos_visitados': len(grafo.movimentos.visitados),
            'num_iteracoes': estatisticas.get('iteracoes', 0),
            'tempo_execucao': tempo_execucao,
            'nos_expandidos': estatisticas.get('nos_expandidos', 0)
        }
    else:
        return {
            'algoritmo': nome_algoritmo,
            'origem': origem,
            'destino': destino,
            'encontrou_caminho': False,
            'caminho': '',
            'custo_total': float('inf'),
            'num_nos_caminho': 0,
            'num_nos_visitados': 0,
            'num_iteracoes': 0,
            'tempo_execucao': tempo_execucao,
            'nos_expandidos': 0
        }

def executar_experimento_completo(arquivo_grafo, origem, destino, num_execucoes=5):
    """Executa todos os algoritmos múltiplas vezes e calcula estatísticas.
    
    Args:
        arquivo_grafo: Caminho do arquivo JSON do grafo
        origem: Nó de origem
        destino: Nó de destino
        num_execucoes: Número de execuções para estatísticas
        
    Returns:
        pandas.DataFrame: DataFrame com todos os resultados
    """
    # Define os algoritmos a serem testados
    algoritmos = [
        (GrafoBFS, 'BFS'),
        (GrafoDFS, 'DFS'),
        (GrafoGananciosa, 'B.Gananciosa'),
        (GrafoAEstrela, 'A*'),
        (GrafosDijkstra, 'Dijkstra')
    ]
    
    resultados = []
    
    print(f"Executando experimento: {origem} -> {destino}")
    print(f"Arquivo do grafo: {arquivo_grafo}")
    print(f"Número de execuções por algoritmo: {num_execucoes}\n")
    
    # Executa cada algoritmo múltiplas vezes
    for classe_grafo, nome_algoritmo in algoritmos:
        print(f"Executando {nome_algoritmo}...")
        
        execucoes = []
        tempos = []
        
        # Executa o algoritmo NUM_EXECUCOES vezes
        for i in range(num_execucoes):
            resultado = executar_algoritmo(classe_grafo, nome_algoritmo, arquivo_grafo, origem, destino)
            execucoes.append(resultado)
            tempos.append(resultado['tempo_execucao'])
        
        # Calcula estatísticas de tempo (que pode variar entre execuções)
        tempo_medio = statistics.mean(tempos)
        tempo_desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0
        
        # Usa os dados da primeira execução como base (caminho, custo, etc. são determinísticos)
        resultado_base = execucoes[0].copy()
        resultado_base['tempo_execucao_medio'] = tempo_medio
        resultado_base['tempo_desvio_padrao'] = tempo_desvio
        resultado_base['num_execucoes'] = num_execucoes
        
        resultados.append(resultado_base)
        
        # Imprime resultado na tela
        if resultado_base['encontrou_caminho']:
            print(f"  Caminho: {resultado_base['caminho']}")
            print(f"  Custo: {resultado_base['custo_total']}")
            print(f"  Nós visitados: {resultado_base['num_nos_visitados']}")
            print(f"  Tempo médio: {tempo_medio:.6f}s (±{tempo_desvio:.6f}s)")
        else:
            print(f"  Caminho não encontrado")
        print()
    
    return pd.DataFrame(resultados)

def criar_pasta_resultados():
    """Cria a pasta 'resultados' se não existir."""
    if not os.path.exists('resultados'):
        os.makedirs('resultados')
        print("Pasta 'resultados' criada.")

def salvar_csv(df, arquivo_grafo, origem, destino):
    """Salva o DataFrame em arquivo CSV na pasta resultados.
    
    Args:
        df: DataFrame com os resultados
        arquivo_grafo: Nome do arquivo do grafo (para nomenclatura)
        origem: Nó de origem
        destino: Nó de destino
        
    Returns:
        str: Caminho do arquivo CSV salvo
    """
    # Extrai o nome base do arquivo (sem caminho e extensão)
    nome_grafo = os.path.splitext(os.path.basename(arquivo_grafo))[0]
    
    # Define o nome do arquivo CSV
    nome_arquivo = f"resultados/{nome_grafo}_{origem}_{destino}.csv"
    
    # Salva o arquivo
    df.to_csv(nome_arquivo, index=False)
    print(f"Resultados salvos em: {nome_arquivo}")
    
    return nome_arquivo

def main():
    """Função principal que executa o experimento completo."""
    print("=== EXPERIMENTO DE COMPARAÇÃO DE ALGORITMOS ===\n")
    
    # Cria pasta de resultados
    criar_pasta_resultados()
    
    # Executa o experimento
    df_resultados = executar_experimento_completo(ARQUIVO_GRAFO, ORIGEM, DESTINO, NUM_EXECUCOES)
    
    # Salva os resultados em CSV
    arquivo_csv = salvar_csv(df_resultados, ARQUIVO_GRAFO, ORIGEM, DESTINO)
    
    # Gera gráficos comparativos
    gerar_graficos(df_resultados, ARQUIVO_GRAFO, ORIGEM, DESTINO)
    
    # Imprime resumo final
    print("\n=== RESUMO DOS RESULTADOS ===")
    print(df_resultados[['algoritmo', 'encontrou_caminho', 'custo_total', 'num_nos_visitados', 'tempo_execucao_medio']].to_string(index=False))
    
    print(f"\n=== EXPERIMENTO CONCLUÍDO ===")
    print(f"Arquivo CSV: {arquivo_csv}")

if __name__ == "__main__":
    main()