# 🎨 Visualização de Grafos - Guia de Uso

## 📋 Resumo

A classe `VisualizacaoGrafo` gera visualizações interativas de algoritmos de busca em grafos usando a biblioteca `pyvis`. 

**Status: ✅ Implementada e funcional**

## 🔧 Principais Funcionalidades

### Cores dos Nós:
- 🔵 **Azul**: Nó de origem
- 🔴 **Vermelho**: Nó de destino  
- 🟢 **Verde**: Nós do caminho encontrado
- 🟡 **Amarelo**: Nós visitados durante a busca
- ⚪ **Cinza**: Nós não visitados

### Arestas:
- 🟢 **Verde espesso**: Arestas do caminho final
- ⚪ **Cinza tracejado**: Outras arestas

### Informações Exibidas:
- Labels descritivos nos nós
- Pesos das arestas
- Estatísticas do algoritmo no título
- Interatividade (zoom, arraste, tooltips)

## 📖 Como Usar

### Uso Básico:
```python
from util_visualizacao import VisualizacaoGrafo
from util_grafos_outros import GrafoBFS

# 1. Criar e executar algoritmo
grafo = GrafoBFS("Meu Grafo")
grafo.carregar_json('base_grafos/grafo_acai.json')
grafo.encontrar_caminho('A', 'J')

# 2. Gerar visualização
viz = VisualizacaoGrafo(grafo, "Busca em Largura")
arquivo = viz.gerar_grafo_visual("resultado", 'A', 'J')

# 3. Abrir no navegador: resultado.html
```

### Uso Básico:
```python
from util_visualizacao import VisualizacaoGrafo
from util_grafos_outros import GrafoBFS

# 1. Criar e executar algoritmo
grafo = GrafoBFS()
grafo.carregar_json('base_grafos/grafo_acai.json')
grafo.encontrar_caminho('A', 'J')

# 2. Gerar visualização
viz = VisualizacaoGrafo(grafo, "Busca em Largura")
arquivo = viz.gerar_grafo_visual("resultado", 'A', 'J')

# 3. Abrir arquivo resultado.html no navegador
```

### Exemplo Completo:
```python
# Executar script principal que gera todas as visualizações
python rodar_experimento.py

# Visualizações são salvas em ./resultados/
# Exemplo: grafo_acai_BFS_A_J.html
```

## 📦 Dependências

### Obrigatória:
- **pyvis** - Instalação automática se não encontrada

### Opcional:
- **selenium** + **ChromeDriver** - Para gerar imagens PNG

```bash
pip install pyvis
# Para PNG (opcional):
pip install selenium
```

## 📁 Arquivos Gerados

Ao executar `rodar_experimento.py`, são criados na pasta `resultados/`:

- **HTML interativos**: `grafo_acai_[ALGORITMO]_A_J.html`
- **Dados CSV**: `grafo_acai_A_J.csv` (métricas de performance)  
- **Gráficos**: `Comparando algoritmos_A_J_graficos.png`

## � Métodos Principais

### `VisualizacaoGrafo(grafo, titulo)`
Cria objeto de visualização a partir de um grafo já executado.

### `gerar_grafo_visual(nome_arquivo, origem, destino)`
Gera arquivo HTML interativo com a visualização colorida.

**Retorna**: Caminho do arquivo HTML gerado

## ✅ Testado e Funcional

A classe está completamente implementada e testada com todos os algoritmos:
- ✅ BFS, DFS, Dijkstra, A*, Busca Gananciosa
- ✅ Cores diferenciadas para nós e arestas
- ✅ Geração automática de arquivos HTML
- ✅ Compatível com diferentes grafos JSON

**Pronto para uso em experimentos de algoritmos de busca!**