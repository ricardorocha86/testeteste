import streamlit as st
from openai import OpenAI
import os

import networkx as nx
import matplotlib.pyplot as plt
import textwrap
import numpy as np
import colorsys
from matplotlib.patches import Ellipse  # Para desenhar ovais


def buscar_aulas(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.txt')]

def ler_aula(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return f.read()

def aux(x):
    return x[:-4]

def gerar_mapa_mental2(conteudo_aula):
    client = OpenAI(api_key=openai_api_key)  
    modelo = 'gpt-4o-mini'  
    prompt_mapa_mental2 = f"""
        Você é um assistente especializado em análise de textos.
        Analise o texto fornecido apresente as 10 principais informações contidas no texto fornecido.
        Cada linha de informação deve conter no máximo 60 caracteres.
        Crie para essas um sistema hierárquico de relacionamento entre elas. Use um nível de hierarquia por linha. 
        Não ponha título nas informações, use apenas a classificação de níveis para mostrar a relação entre elas. 
        Use ' ## ' no nível 2, e ' ### ' no nível 3, e assim por diante. Não use itemização.
        Desprese o item do texto fornecido referente a discuções e estudos de caso. 
        Não siga a extruturação do texto fornecido, crie uma nova que atenda aos critérios de tamanho do output.
        Resuma o texto fornecido de maneira a que o output tenha no máximo 12 linhas. É mandatório que a resposta tenha no máximo 12 linhas.
        Use negrito para destacar os tópicos principais e itálico para os subtópicos.
        O texto fornecido é:
        {conteudo_aula}
        """
    stream = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt_mapa_mental2}]
    )
    return stream.choices[0].message.content

#def exibir_mapa_mental(mapa_mental):
#        st.markdown(mapa_mental)

# Configuração principal
diretorio_aulas = 'Aulas'
aulas = buscar_aulas(diretorio_aulas)

# Widgets
aula_selecionada = st.sidebar.selectbox(
    'Selecione uma aula:', 
    sorted(aulas), 
    index=0, 
    format_func=aux
)

# Carregar conteúdo
caminho_aula = os.path.join(diretorio_aulas, aula_selecionada)
conteudo_aula = ler_aula(caminho_aula)
openai_api_key = st.secrets["OPENAI_API_KEY"]  # Garantir que está usando o segredo
# Botão de geração

markdown_text = gerar_mapa_mental2(conteudo_aula) 


def parse_markdown_to_graph(md_text):
    """
    Processa o texto Markdown e gera um grafo hierárquico.
    Cada nó recebe um atributo 'level' que indica seu nível na hierarquia.
    """
    lines = md_text.split("\n")
    graph = nx.DiGraph()
    stack = []  # Pilha para acompanhar a hierarquia

    for line in lines:
        if not line.strip():
            continue

        level = line.count("#")  # Determina o nível com base no número de '#'
        title = line.replace("#", "").strip()

        # Mantém apenas os elementos da hierarquia até o nível atual
        if len(stack) >= level:
            stack = stack[:level-1]

        # Adiciona o nó com o atributo 'level'
        graph.add_node(title, level=level)

        # Conecta com o nó pai, se existir
        if stack:
            graph.add_edge(stack[-1], title)

        stack.append(title)

    return graph

def assign_colors(G, root, base_color_hsv=(0.6, 0.5, 0.95), delta_h=0.1, delta_h2=0.3, brightness_factor=0.9):
    """
    Atribui cores aos nós do grafo de forma hierárquica.
    
    Para o nó raiz, a cor é definida por base_color_hsv. Para os nós filhos
    do nó raiz (nível 2), utiliza-se um delta de matiz maior (delta_h2)
    para diferenciar as cores de maneira mais acentuada; para os demais níveis,
    utiliza-se um delta menor (delta_h). O fator de brilho reduz a luminosidade
    dos nós filhos em relação ao pai.
    """
    colors = {}
    colors[root] = base_color_hsv  # Cor base para o nó raiz

    def dfs(node):
        children = list(G.successors(node))
        n = len(children)
        if n == 0:
            return
        parent_color = colors[node]
        new_v = parent_color[2] * brightness_factor  # Reduz a luminosidade para os filhos
        # Se o nó atual for de nível 1, os filhos (nível 2) terão variação mais acentuada
        effective_delta = delta_h2 if G.nodes[node]['level'] == 1 else delta_h
        for i, child in enumerate(children):
            hue_offset = (i - (n - 1) / 2) * effective_delta if n > 1 else 0
            new_h = (parent_color[0] + hue_offset) % 1.0
            new_s = parent_color[1]
            colors[child] = (new_h, new_s, new_v)
            dfs(child)

    dfs(root)
    return colors



# Cria o grafo a partir do Markdown
G = parse_markdown_to_graph(markdown_text)

# Identifica o nó raiz (nível 1)
root_nodes = [node for node, data in G.nodes(data=True) if data.get('level', 0) == 1]
if root_nodes:
    root = root_nodes[0]
else:
    root = list(G.nodes())[0]

# Atribui cores hierárquicas: os nós filhos do nó raiz (nível 2) terão variações mais acentuadas
colors_hsv = assign_colors(G, root)
color_map = {node: colorsys.hsv_to_rgb(*hsv) for node, hsv in colors_hsv.items()}

# Define o layout radial utilizando o Graphviz (programa 'twopi') com o nó raiz centralizado
pos = nx.nx_agraph.graphviz_layout(G, prog='twopi', args=f'-Groot="{root}"')
# Inverte o eixo Y para centralizar o nó raiz
for node, (x, y) in pos.items():
    pos[node] = (x, -y)

plt.figure(figsize=(14, 10))
ax = plt.gca()
ax.set_aspect('equal')

# Desenha as arestas
nx.draw_networkx_edges(
    G,
    pos,
    edge_color='gray',
    arrows=True,
    arrowstyle='-|>',
    arrowsize=12,
    node_size=0,
    connectionstyle='arc3,rad=0.1',
    ax=ax
)

# Desenha os nós como ovais com texto centralizado e dimensões ajustadas ao conteúdo
for node, (x, y) in pos.items():
    wrapped_text = textwrap.wrap(node, width=20)
    max_line_length = max([len(line) for line in wrapped_text], default=0)
    # Fatores de escala ajustados para o layout radial:
    width = max_line_length * 6.0
    height = len(wrapped_text) * 20.0
    oval = Ellipse((x, y), width=width, height=height,
                   facecolor=color_map[node],
                   edgecolor='black', lw=1, alpha=0.9)
    ax.add_patch(oval)
    plt.text(x, y, "\n".join(wrapped_text),
             fontsize=8, ha='center', va='center',
             fontweight='bold', linespacing=1.2)



plt.title("Mapa Mental", fontsize=14, pad=20)
plt.axis('off')
plt.tight_layout()
plt.show()
st.pyplot(plt)