import streamlit as st
import mysql.connector as conn
import pandas as pd
from datetime import date
import calendar
import locale

# Tenta configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # Windows
    except:
        st.warning("⚠️ Não foi possível configurar o locale para pt-BR. Os nomes dos meses podem aparecer em inglês.")

# Função para obter o primeiro e o último dia do mês atual
def get_month_date_range():
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return first_day, last_day

# Inicializa session_state se necessário
if "dados_carregados" not in st.session_state:
    st.session_state["dados_carregados"] = False
if "df" not in st.session_state:
    st.session_state["df"] = None

# Datas padrão
start_default, end_default = get_month_date_range()

# Layout
st.title("📅 Filtro de Datas")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    start_date = st.date_input("Data de Início", value=start_default, format="DD/MM/YYYY")

with col2:
    end_date = st.date_input("Data de Fim", value=end_default, format="DD/MM/YYYY")

with col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Espaço para alinhar o botão
    atualizar = st.button("🔄 Atualizar Dados")

# Subtítulo com datas por extenso (pode aparecer em inglês se locale falhar)
st.subheader(
    f"Dados de {start_date.strftime('%d de %B de %Y')} até {end_date.strftime('%d de %B de %Y')}"
)

# Função que busca os dados no banco
def buscar_dados(data_inicio, data_fim):
    try:
        mydb = conn.connect(
            host="dboperacaobda.mysql.uhserver.com",
            user="usroperacaobda",
            password="i96d1e8zq9@",
            database="dboperacaobda"
        )
        cursor = mydb.cursor()

        sqlQuery = """
            SELECT * 
            FROM geracao_voucher 
            WHERE data_venda BETWEEN %s AND %s
        """
        cursor.execute(sqlQuery, (data_inicio, data_fim))
        rows = cursor.fetchall()

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=colnames)

        return df
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        return pd.DataFrame()

# Primeira carga automática
if not st.session_state["dados_carregados"]:
    df = buscar_dados(start_default, end_default)
    st.session_state["df"] = df
    st.session_state["dados_carregados"] = True

# Atualizar via botão
if atualizar:
    df = buscar_dados(start_date, end_date)
    st.session_state["df"] = df

# Mostrar dados
if st.session_state["df"] is not None:
    if len(st.session_state["df"]) > 0:
        st.success(f"{len(st.session_state['df'])} registros encontrados.")
    else:
        st.warning("Nenhum registro encontrado para o período selecionado.")
    st.dataframe(st.session_state["df"], use_container_width=True)
