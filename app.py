import streamlit as st
import os
import tempfile
from langchain_core.messages import HumanMessage, AIMessage
from Drafter import create_agent

st.set_page_config(page_title="Drafter AI", page_icon="📝")

st.title("📝 Drafter AI Assistant")

# Inicializa o agente na sessão (cache para não recarregar o modelo toda vez)
if "agent" not in st.session_state:
    with st.spinner("Carregando modelos (GPT & Whisper)..."):
        st.session_state.agent = create_agent()

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar para Upload de Áudio
with st.sidebar:
    st.header("🎤 Áudio")
    
    # Tabs para organizar
    tab1, tab2 = st.tabs(["Upload", "Microfone"])
    audio_data = None

    with tab1:
        uploaded_file = st.file_uploader("Envie um áudio", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            audio_data = uploaded_file
    
    with tab2:
        mic_data = st.audio_input("Grave sua voz")
        if mic_data:
            audio_data = mic_data
    
    if audio_data:
        st.audio(audio_data)
        
        # Salva o arquivo temporariamente para o Whisper ler
        file_ext = audio_data.name.split('.')[-1] if hasattr(audio_data, 'name') else "wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
            tmp_file.write(audio_data.getvalue())
            tmp_path = tmp_file.name
        
        if st.button("Transcrever e Inserir"):
            # Adiciona uma mensagem oculta instruindo o agente a usar a ferramenta
            instruction = f"Por favor, transcreva o áudio localizado neste caminho: {tmp_path}"
            st.session_state.messages.append(HumanMessage(content=instruction))
            
            # Processa imediatamente
            with st.spinner("Transcrevendo e processando..."):
                inputs = {"messages": st.session_state.messages}
                result = st.session_state.agent.invoke(inputs)
                st.session_state.messages = result["messages"]
                # Força recarregamento para mostrar a resposta
                st.rerun()

# Exibe mensagens do chat
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Input do usuário
if prompt := st.chat_input("Como posso ajudar com seu documento?"):
    # Adiciona mensagem do usuário
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Executa o agente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            inputs = {"messages": st.session_state.messages}
            # Usamos invoke para pegar o estado final
            result = st.session_state.agent.invoke(inputs)
            
            # Atualiza o histórico com todas as mensagens (incluindo tool calls intermediários se necessário, 
            # mas aqui focamos no resultado final)
            st.session_state.messages = result["messages"]
            
            # Pega a última mensagem da IA para exibir
            last_msg = result["messages"][-1]
            if isinstance(last_msg, AIMessage):
                st.markdown(last_msg.content)