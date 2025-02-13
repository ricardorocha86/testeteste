import streamlit as st
import os
import pandas as pd 
import re
from openai import OpenAI 


st.markdown('✨**Conteúdo de Aula** - selecione a aula na barra lateral e use os recursos AI ao fim do conteúdo selecionado.')
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


# Função para buscar arquivos markdown no diretório de aulas
def buscar_aulas(diretorio):
    return [f for f in os.listdir(diretorio) if f.endswith('.txt')]

# Função para ler o conteúdo de uma aula em markdown
def ler_aula(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return f.read()

# Diretório onde as aulas estão armazenadas
diretorio_aulas = 'Aulas' 

# Busca as aulas no diretório
aulas = buscar_aulas(diretorio_aulas)

def aux(x):
    return x[:-4]
# Widget de seleção de aula
aula_selecionada = st.sidebar.selectbox('Selecione uma aula:', sorted(aulas), index = 0, format_func = aux)
 
caminho_aula = os.path.join(diretorio_aulas, aula_selecionada)
conteudo_aula = ler_aula(caminho_aula)
st_markdown(conteudo_aula)

def perfil_do_aluno(aluno):
    return f"""
        Ano de entrada no curso de Engenharia Mecânica: {aluno.entrada}.
        As áreas de interesse dentro do curso de Engenharia Mecânica são: {aluno.interesse}.
        O nível de conhecimento na área de Ciências dos Materiais é: {aluno.conhecimento}.
        A participaçãoo em projetos práticos ou pesquisas aplicadas é: {aluno.projetos}.
        O objetivos ao se formar é: {aluno.objetivo}.
        O formato de estudo preferido é: {aluno.estudo}.
        A participação em Atividades Extracurriculares é: {aluno.extra}.
        A autoavaliação do desempenho Acadêmico é: {aluno.desempenho}.
        As expectativas e sugestões em relação à Disciplina de Ciência dos Materiais são {aluno.expectativas}.
        """


dados = pd.read_csv('Alunos2.csv')

# Widget de seleção de aluno
aluno_selecionado = st.sidebar.selectbox('Selecione um aluno:', sorted(dados.nome), index = 0)
aluno = dados[dados['nome'] == aluno_selecionado]
perfil = perfil_do_aluno(aluno)

dificuldade_selecionada = st.sidebar.selectbox('Selecione a dificuldade dos exercícios:', {'Fácil', 'Média', 'Difícil', 'Muito Difícil'})


st.divider()
abas = ['Exercícios AI', 'Lista de Insights AI']

aba1, aba2 = st.tabs(abas)

with aba1:
    st.header(abas[0]) 

    if st.button('✨ Gerar Lista de Exercícios dessa Lição', type = 'primary'): 

        # Configurações de API 
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=openai_api_key)
        modelo = 'gpt-4o-mini'
         
        # Mensagem inicial do assistente no chat
        prompt = f"""
        Você é um assistente de professor da disciplina Ciência dos materiais, para o curso de engenharaia, cuja tarefa é escrever uma lista de exercicios baseado no <material de aula> abaixo. 
        Não se limite aos exemplos do <material de aula>, use outros exemplos que sejam pertinentes.
        Você deve fazer 3 exercícios abertos (discursivos) e 3 exercícios de teste (objetivos). Nos abertos, deve ser feita uma pergunta aberta. 
        Nos exercicios do tipo teste, deve ter uma pergunta e 4 alternativas de resposta, da qual apenas uma seja correta.
        Cada alternativa deve estar em uma linha. 
        Não diga qual resposta é a correta. 
        A dificuldade dos exercícios deve ser <dificuldade>. Não diga qual a dificuldade do exercício.
        Cada exercício deve ter a maior afinidade possível com o <perfil> do aluno abaixo, isto é, deve ser personalizado.
        O output deve conter os 3 exercicios abertos seguidos dos 3 exercicios de teste, seguido de uma breve resolução dos exercícios abertos e o gabarito dos exercicios de teste, separados por sessão. 
        No seu output, deve contar apenas o exercício, nada a mais, nada a menos. 
        Use formatação quando necessário, use negrito e italico para destacar o que for importante e emojis quando pertinente. 

        <material de aula>
        {conteudo_aula}
        </material de aula>

        <perfil>
        {perfil_do_aluno}
        </perfil>    

        <dificuldade>
        {dificuldade_selecionada}
        </dificuldade>    
         """ 

        # Faz uma requisição à API OpenAI para gerar a resposta do assistente
        with st.chat_message("assistant", avatar = '👨🏼‍🏫'):
            stream = client.chat.completions.create(
                model=modelo,
                messages= [{"role": "user", "content": prompt}],
                stream=True
            )

            # Exibe a resposta em tempo real
            response = st.write_stream(stream)


with aba2:
    st.header(abas[1]) 

    if st.button('✨ Gerar Lista de Insights dessa Aula', type = 'primary'): 

        # Configurações de API 
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=openai_api_key)
        modelo = 'gpt-4o-mini'
         
        # Mensagem inicial do assistente no chat
        prompt = f"""Você é um assistente de professor da disciplina Ciência dos materiais, para o curso de engenharaia, que tem a função de utilizar o <material de aula> e processar seguindo as seguintes instruções:
        - Leia e compreenda integralmente o material de aula para captar o contexto, os tópicos abordados e a progressão dos conceitos.
        - Escreva um output que seja uma coleção de 10 insights sobre a aula.
        - Use bullet points para cada insight. 
        - use texto normal nos titulos das sessões. 
        - cada insight deve ter no máximo 140 caracteres.
        - seu output deve ser apenas, e somente apenas, a lista de insights.
        - use negrito e italico para destacar o que for importante.
        - Não se limite aos exemplos do <material de aula>, use outros exemplos que sejam pertinentes.
        Estes insights ainda devem ser de tal forma a correlacionar o <material de aula> com as expectativas apresentadas no <perfil> do aluno. 
         
        O material da aula é o seguinte:
        <material de aula>
        {conteudo_aula}
        </material de aula>

        O perfil do aluno é o seguinte:
        <perfil>
        {perfil_do_aluno}
        </perfil> 
        """

        # Faz uma requisição à API OpenAI para gerar a resposta do assistente
        with st.chat_message("assistant", avatar = '👨🏼‍🏫'):
            stream = client.chat.completions.create(
                model=modelo,
                messages= [{"role": "user", "content": prompt}],
                stream=True
            )

            # Exibe a resposta em tempo real
            response = st.write_stream(stream)
            
 
