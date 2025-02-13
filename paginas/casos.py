import streamlit as st
import os
import pandas as pd 
import re
from openai import OpenAI 


st.markdown('✨**Estudo de Casos** - selecione um Estudo de Caso na barra lateral e use os recursos AI ao fim do conteúdo selecionado.')
st.divider()

def st_markdown(markdown_string):
    parts = re.split(r"!\[(.*?)\]\((.*?)\)", markdown_string)
    for i, part in enumerate(parts):
        if i % 3 == 0:
            st.markdown(part)
        elif i % 3 == 1:
            title = part
        else:
            st.image(part)  # Add caption if you want -> , caption=title)


# Função para buscar arquivos markdown no diretório de casos
def buscar_casos(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.txt')]

# Função para ler o conteúdo de um caso em markdown
def ler_caso(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return f.read()

# Diretório onde ao casos estão armazenados
diretorio_casos = 'Casos' 

# Busca ao casos no diretório
casos = buscar_casos(diretorio_casos)

def aux(x):
    return x[:-4]
# Widget de seleção de caso
caso_selecionado = st.sidebar.selectbox('Selecione um Estudo de Caso:', sorted(casos), index = 0, format_func = aux)
 
caminho_caso = os.path.join(diretorio_casos, caso_selecionado)
conteudo_caso = ler_caso(caminho_caso)
st_markdown(conteudo_caso)

st.divider()

openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)
modelo = 'gpt-4o-mini'
         

### resposta
     
resposta = st.text_area('Escreva aqui sua resposta')

def barema (conteudo_caso, resposta):
    return f"""
        Avalie a {resposta} dada pelo aluno em função do exercício proposto {conteudo_caso}.
        Se a resposta do aluno contemplar a maioria dos pontos que respondem a questão, uma mensagem de parabenização deve ser dada. 
        Se a resposta do aluno contemplar a minoria dos pontos que respondem a questão, uma mensagem de insentivo deve ser dada.
        Aponte os erros cometidos e a solução que deveria ter sido dada.
        Use um tom amigável. Use negrito e itálico para destacar partes importantes. Use emojis para tornar os comentários mais agradáveis.
        Incentive responder um novo exercício.
        """

if st.button("Corrigir", type = 'secondary'):
    correcao = barema(conteudo_caso, resposta)
    print(correcao)
    stream = client.chat.completions.create(
        model=modelo,
        messages= [{"role": "user", "content": correcao}],
        stream=True
    )
        # Exibe a resposta em tempo real
    response = st.write_stream(stream)
    if st.button("Tentar Novamente", type = 'secondary'):
       print("Ok")


