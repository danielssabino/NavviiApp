import mysql.connector as conn
import pandas as pd
from datetime import date

# Variáveis globais corretamente definidas no escopo do módulo
global_dbUser = None
global_dbDataBase = None

global_df_resumo_vendas = None
global_df_comissao_prof_tecnicas = None
global_df_comissao_vendas_detalhada = None
global_df_metas_unidade_diario = None
global_df_voucher_wordpress = None


def LoadData(user, database, data_inicio, data_fim):
    global global_dbUser, global_dbDataBase
    global_dbUser = user
    global_dbDataBase = database

    mydb, cursor = conectarDB()

    global global_df_atendimentos 

    global_df_atendimentos = load_atendimentos(mydb, cursor, data_inicio, data_fim)
    

    desconectarDB(mydb, cursor)



def conectarDB():
    
    global global_dbUser, global_dbDataBase
    
    try:
        mydb = conn.connect(
            host="dboperacaobda.mysql.uhserver.com",
            #user="usrgoldensquare", #usrgoldensquare       -usroperacaobda
            user=global_dbUser,
            password="i96d1e8zq9@",
            #database="dbgoldensquare" #dbgoldensquare     - dboperacaobda
            database=global_dbDataBase
        )
        cursor = mydb.cursor()
        return mydb, cursor
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None, None


def desconectarDB(mydb, cursor):
    if cursor:
        cursor.close()
    if mydb:
        mydb.close()


def load_generico(tabela, campoData, mydb, cursor, data_inicio, data_fim):
    if not cursor:
        return pd.DataFrame()
    
    sqlQuery = f"""
        SELECT * 
        FROM {tabela} t
        WHERE t.{campoData} BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    #desconectarDB(mydb, cursor)
    return df


def load_atendimentos(mydb, cursor, data_inicio, data_fim):
    return load_generico("atendimentos", "data", mydb, cursor, data_inicio, data_fim)


def atendimentos_do_dia():
    global global_df_atendimentos
    
    # 🔍 Filtro: status ≠ Cancelado ou Desmarcado
    retorno = global_df_atendimentos[~global_df_atendimentos["status"].isin(["Cancelado", "Desmarcado"])]

    # ⏱️ Ordena pelo campo TIME corretamente 
    retorno = retorno.sort_values("horario_time")

    retorno = retorno[["horario_str", "cliente", "servico", "sala"]].rename(columns={
                "horario_str": "Horário",
                "cliente": "Cliente",
                "servico": "Terapia",
                "sala": "Sala"
            }) 

    return retorno


def formatar_reais(valor):
    """
    Formata um número float para o padrão brasileiro de moeda:
    R$ 1.234,56
    """
    if pd.isna(valor):
        return "R$ 0,00"
    
    try:
        return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return "R$ 0,00"