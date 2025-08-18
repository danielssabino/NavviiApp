import streamlit as st
from dashboard_diario import DashDiario

# Usuários cadastrados (email: senha)
usuarios = {
    "recepcao@buddhags.com.br": {"senha": "GoldenSquare@25", "pagina": "DashDiario", "unidade":"GoldenSquare", "user":"usrgoldensquare", "database":"dbgoldensquare"},
    "recepcao@buddhaps.com.br": {"senha": "PartageSantana@25", "pagina": "DashDiario", "unidade":"PartageSantana", "user":"usroperacaobda", "database":"dboperacaobda"},
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
            st.session_state.unidade = usuarios[email]["unidade"]
            st.session_state.dbUser = usuarios[email]["user"]
            st.session_state.dbDataBase = usuarios[email]["database"]
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")

def router():
    if st.session_state.pagina_destino == "DashDiario":
        DashDiario(st.session_state.unidade,st.session_state.dbUser,st.session_state.dbDataBase)
    #elif st.session_state.pagina_destino == "PartageDashDiario":
        #DashDiario(st.session_state.unidade)
    else:
        st.warning("Página não encontrada.")

# Execução
if not st.session_state.logado:
    login()
else:
    router()
