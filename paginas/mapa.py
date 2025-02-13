import streamlit as st
from openai import OpenAI
import os

def buscar_aulas(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.txt')]

def ler_aula(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return f.read()

def aux(x):
    return x[:-4]

def gerar_mapa_mental(conteudo_aula):
    client = OpenAI(api_key=openai_api_key)  
    modelo = 'gpt-4o-mini'  
    prompt_mapa_mental = f"""
        Você é um assistente especializado em criar mapas mentais.
        Analise o texto fornecido e crie um mapa mental em formato de texto, usando um sistema hierárquico.
        Use um nível de hierarquia por linha. Use ' ## ' no nível 2, e ' ### ' no nível 3, e assim por diante.
        Use no máximo 3 níveis hierárquicos.
        Use negrito para destacar os tópicos principais e itálico para os subtópicos.
        O texto fornecido é:
        {conteudo_aula}
        """
    stream = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt_mapa_mental}],
        stream=True
    )
    response = st.write_stream(stream)
    return response

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
if st.button('✨ Gerar Mapa Mental', type='primary'):
    mapa_mental = gerar_mapa_mental(conteudo_aula)
    # exibir_mapa_mental(mapa_mental)