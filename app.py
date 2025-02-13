import streamlit as st


st.set_page_config(
    page_title="Ciência dos Materiais - Aplicativo de Aula",
    page_icon="⚛️",
    layout="centered",
    initial_sidebar_state="expanded")
 
paginas = {"Páginas": [
        st.Page("paginas/aulas.py", title="Aulas", icon='📚'), 
        st.Page("paginas/chatbot.py", title="Jeffbot", icon='👨🏼‍🏫'), 
        st.Page("paginas/kahoot2.py", title="Kahoot", icon='🎯'), 
        st.Page("paginas/mapa.py", title = "Mapas Mentais", icon = '💬'),
        st.Page("paginas/mapa2.py", title = "Mapas Mentais - Gráfico", icon = '💬'),        
        st.Page("paginas/casos.py", title = "Estudos de Casos", icon = '💡'),  
        st.Page("paginas/feedback.py", title = "Feedback", icon = '🦏')
    ],
    "Outras Páginas": [
        st.Page("paginas/inicial.py", title="Início", default = True, icon='🏠'), 
    ], 
}


pg = st.navigation(paginas)
pg.run()

