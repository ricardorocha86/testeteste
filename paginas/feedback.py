import streamlit as st
import os
import pandas as pd 
import re
from openai import OpenAI 
from pydantic import BaseModel
from typing import Literal

st.subheader("Oie - Deixe seu Comentário sobre a Aula:")

# Coleta do nome, comentário e nota do aluno
nome = st.text_input("Seu nome:")
comentario = st.text_area("Seu comentário:")
st.write('Avalie o app:')
nota = st.feedback("stars")
#st.write(nota)



def analisar_feedback(nome, comentario, nota):
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=openai_api_key)

    texto = f"""
    O nome do aluno é: {nome} e fez o seguinte comentário: "{comentario}" e deu a seguinte nota: {nota + 1}. 
    """
    #st.write(texto)

    class Pedido(BaseModel):
        sentimento: Literal['elogio', 'reclamação', 'sugestão', 'crítica construtiva', 'reconhecimento']
        resposta: str
        plano: list[str]

    instrucoes = """
    Voce é um analisador de feedback que os alunos dão ao utilizar uma nova ferramenta de ensino. 
    Voce recebera um texto com as informacoes do aluno, seu feedback e a nota dada para o app.
    Sua tarefa é analisar o sentimento do feedback e classifica-lo em uma das categorias:
    - elogio: quando se reconhece algo positivo, tipo um bom trabalho ou uma atitude legal. é aquele "vc arrasou nisso aí" ou "mandou bem demais".
    - reclamação: quando há algo que não agradou, e a pessoa quer que isso mude. tipo "isso aqui não ficou legal, precisa melhorar".
    - sugestão: mais suave, onde se propõe algo para melhorar sem deixar claro que está ruim. "seria massa se pudesse fazer assim...".
    - crítica construtiva: é tipo a reclamação, mas com foco em como melhorar, trazendo uma solução, "acho que poderia fazer de outra forma, assim ficaria melhor".
    - reconhecimento: aqui se destaca o valor da pessoa ou do trabalho, "muito bom seu esforço, isso faz diferença".

    Além disso, você vai propor uma resposta adequada, e propor um plano de ações de melhoria em caso do feedback ser construtivo ou reclamação.
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instrucoes},
            {"role": "user", "content": texto},
        ],
        response_format=Pedido,
    )

    event = completion.choices[0].message.parsed
    return dict(event)



def processar_feedback(dados):
    sentimento = dados['sentimento']
    resposta = dados['resposta']
    plano = "\n".join([f"- {item}" for item in dados['plano']])
    
    texto = f"""
    **Processamento do Feedback** 
    Identificamos que o sentimento registrado foi: **{sentimento}**. 
    Possível resposta ao feedback:     {resposta}
    Nosso plano de ação é o seguinte:
    {plano}

    """

    return texto


if st.button("Enviar Feedback", type='primary'):
    st.divider()
    retorno = dict(analisar_feedback(nome, comentario, nota))
    st.write(f"Identificamos que o sentimento registrado foi: **{retorno['sentimento'].upper()}**.")
    st.write(f"Possível resposta ao feedback: **{retorno['resposta']}**.")
    st.write("Ações sugeridas:")
    for item in retorno['plano']:
        st.write(f"- {item}")
    #st.success("Feedback enviado com sucesso!")
    #função para enviar o feedback para o email do dono do app