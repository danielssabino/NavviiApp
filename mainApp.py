import streamlit as st
from partagesantana_dash_diario import partageSantanaDash
from goldensquare_dash_diario import goldensquareDash

# Usuários cadastrados (email: senha)
usuarios = {
    "recepcao@buddhags.com.br": {"senha": "GoldenSquare@25", "pagina": "GoldenDashDiario"},
    "recepcao@buddhaps.com.br": {"senha": "PartageSantana@25", "pagina": "PartageDashDiario"},
}

# Inicializa sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pagina_destino" not in st.session_state:
    st.session_state.pagina_destino = None

def login():
    st.title("🔐 Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email in usuarios and senha == usuarios[email]["senha"]:
            st.session_state.logado = True
            st.session_state.usuario = email
            st.session_state.pagina_destino = usuarios[email]["pagina"]
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")

def router():
    if st.session_state.pagina_destino == "GoldenDashDiario":
        goldensquareDash()
    elif st.session_state.pagina_destino == "PartageDashDiario":
        partageSantanaDash()
    else:
        st.warning("Página não encontrada.")

# Execução
if not st.session_state.logado:
    login()
else:
    router()
