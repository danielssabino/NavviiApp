import streamlit as st
import pandas as pd
from datetime import date, timedelta
import dashboard_AtendimentosDia_indicadores as dIndicadores
import calendar

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_inteiro(valor):
    return f"{valor:,}".replace(",", ".")

def formatar_decimal(valor):
    if pd.isna(valor):  # evita erro com NaN
        return "-"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def Atendimentos(unidade, dbUser, dbDataBase):
    st.set_page_config(layout="wide")
    #st.set_page_config(layout="centered")

    unidadeDesc = ""
    if unidade == "GoldenSquare":
        unidadeDesc = "Golden Square"
    elif unidade == "PartageSantana":
        unidadeDesc = "Partage Santana"
    
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout"):
            for key in ["logado", "usuario", "pagina_destino", "unidade", "dbUser", "dbDataBase"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # CSS corrigido
    card_style = """
        <style>
            .card {
                background-color: #f9f9f9;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                font-size: 17px;
            }
            .card-line {
                display: flex;
                justify-content: space-between; /* coloca lado a lado */
                align-items: center;
                margin: 4px 0;
            }
            .card-line p {
                margin: 0;
                flex: 1; /* divide espaço igualmente */
            }
        </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    # 📌 Descobre primeiro e último dia do mês atual
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
    
    dIndicadores.LoadData(dbUser, dbDataBase,hoje, hoje)

    # Título e seleção de data
    st.title("🗕️ Atendimentos do dia - " + unidadeDesc)
    st.markdown(f"📅 {hoje.strftime('%d/%m/%Y')}")

    try:
        df = dIndicadores.atendimentos_do_dia()

        if df.empty:
            st.info("Nenhum atendimento válido registrado para hoje.")
        else:
            for _, row in df.iterrows():
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-line">
                            <p>🕒 <strong>{row['Horário']}</strong></p>
                            <p>👤 <strong>{row['Cliente']}</strong></p>
                        </div>
                        <div class="card-line">
                            <p>🧠 <strong>{row['Terapia']}</strong></p>
                            <p>🏠 <strong>{row['Sala']}</strong></p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"Erro ao carregar atendimentos: {e}")

    st.divider()

    