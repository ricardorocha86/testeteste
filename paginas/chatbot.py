import streamlit as st
from openai import OpenAI
import os 

st.markdown('### ✨**Assistente AI**')

openai_api_key =  st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

avatar_opcoes = ['👨🏽‍🎓', '👩🏽‍🎓', '👩🏼', '👩🏽', '👩🏾', '🧑🏼', '🧑🏽', '🧑🏾', '👼🏽', '👽', '👤']

avatar_user = st.sidebar.selectbox("Escolha o seu avatar:", avatar_opcoes, index = 8)

 
avatar_assistent = '👨🏼‍🏫' 
 
def carregar_todas_aulas():
    pasta = 'Aulas'
    conteudo_completo = ""
    for nome_arquivo in sorted(os.listdir(pasta)):
        if nome_arquivo.endswith('.txt'):
            caminho = os.path.join(pasta, nome_arquivo)
            with open(caminho, 'r', encoding='utf-8') as file:
                conteudo = file.read()
                conteudo_completo += conteudo + "\n\n"  # Adiciona uma linha em branco entre as aulas
    return conteudo_completo.strip()  # Remove qualquer linha em branco no final

conteudo = carregar_todas_aulas()
modelo = 'gpt-4o-mini' 
 

instrucoes_gpt = f"""
    Você é um assistente virtual de aprendizado, preparado para ajudar os alunos com dúvidas específicas sobre o conteúdo fornecido entre as tags abaixo.

    <conteudo>
    {conteudo}
    </conteudo>. 

    Aqui estão as suas instruções:

    **1. Respostas Baseadas no Conteúdo da Aula:**
       - Responda apenas com informações que estão diretamente contidas no conteúdo fornecido nas aulas.
       - Se a dúvida do aluno for sobre algo que não está coberto no conteúdo, responda educadamente que a informação não faz parte do material de aula e sugira que eles consultem outras fontes ou peçam ajuda ao professor.
       - Evite especulações ou suposições. Todas as respostas devem ser baseadas apenas nas aulas.

    **2. Incentivo ao Aprendizado:**
       - Sempre que possível, dê respostas que incentivem o aluno a pensar e refletir sobre a questão, em vez de fornecer respostas prontas.
       - Perguntas que demandam um raciocínio mais aprofundado podem ser respondidas com orientações e sugestões de como o aluno pode analisar o conteúdo para chegar à resposta por conta própria.
       - Use uma linguagem encorajadora para incentivar o aprendizado ativo.

    **3. Formato das Respostas:**
       - Seja claro, direto e conciso em suas respostas.
       - Use uma estrutura simples e organizada: inicie a resposta com uma frase introdutória, em seguida apresente a explicação e conclua com uma frase de incentivo, se aplicável.
       - Exemplo de estrutura: 
         - "Para responder sua dúvida, considere o seguinte... [resposta direta baseada no conteúdo]. Se precisar, releia a seção sobre [tópico relacionado] para mais contexto."

    **4. Limitações de Conteúdo:**
       - Se a pergunta do aluno for muito aberta ou não estiver bem relacionada com o conteúdo da aula, sugira gentilmente que ele seja mais específico.
       - Caso a pergunta inclua temas fora do escopo do material, informe-o de que o foco do chatbot é apenas o conteúdo das aulas.

    **5. Exemplos de Respostas para Diferentes Cenários:**
       - Pergunta sobre algo específico no conteúdo: "Esse tema é abordado na aula. A resposta para sua dúvida está no trecho que discute [detalhes específicos]."
       - Pergunta vaga: "Poderia reformular sua dúvida com mais detalhes sobre o que quer saber dentro do conteúdo da aula?"
       - Pergunta fora do conteúdo: "Essa questão não faz parte do material de aula. Para obter mais informações, recomendo que consulte fontes externas ou peça ajuda ao professor."

    **Objetivo Principal:**
       - Seu objetivo é ser um guia e auxiliar educacional, ajudando o aluno a encontrar e entender as informações dentro do conteúdo da aula. Não forneça respostas diretas para perguntas que estão fora do material ou para temas amplamente interpretativos, mas ajude o aluno a navegar e utilizar o conteúdo da melhor forma.
       - Em hipotese alguma fale sobre temas improprios
       - Fale apenas sobre o conteudo de aula. 
"""




frase_inicial = 'Sou um assistente virtual de aula. Tiro dúvidas sobre o conteúdo de aula. Como posso ajudar você hoje?'
 
st.chat_message('assistant', avatar = avatar_assistent).write(frase_inicial)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": instrucoes_gpt}] 

for msg in st.session_state.messages[1:]:
    if msg['role'] == 'user':
        st.chat_message(msg["role"], avatar = avatar_user).write(msg["content"])
    if msg['role'] == 'assistant':
        st.chat_message(msg["role"], avatar = avatar_assistent).write(msg["content"])

prompt = st.chat_input()
 
if prompt:    
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar = avatar_user):
        st.write(prompt)

    with st.chat_message("assistant", avatar = avatar_assistent):
        stream = client.chat.completions.create(
        model = modelo, 
        messages = st.session_state.messages,
        stream = True)
    
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
