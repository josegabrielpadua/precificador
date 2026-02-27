import streamlit as st
from google_ai.ai import AIGoogle


def render() -> None:
    """Renderiza o chat com a IA."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if texto := st.chat_input("Diga alguma coisa"):
        st.session_state.chat_history.append({"role": "user", "content": texto})

        ai = AIGoogle(
            prompt_user=(
                "Considerando que em suas respostas você será educado, cordial e respeitoso, "
                "considere o contexto abaixo"
            ),
            response=texto,
        )
        resposta = ai.interaction()
        st.session_state.chat_history.append({"role": "assistant", "content": resposta.content})

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
