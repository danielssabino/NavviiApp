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

    global global_df_resumo_vendas, global_df_comissao_prof_tecnicas 
    global global_df_comissao_vendas_detalhada, global_df_voucher_wordpress
    global global_df_metas_unidade_diario, global_df_metas_unidade_diario_vendas_acumulado 


    global_df_resumo_vendas = load_resumo_vendas(mydb, cursor, data_inicio, data_fim)
    global_df_comissao_prof_tecnicas = load_comissao_prof_tecnicas(mydb, cursor, data_inicio, data_fim)
    global_df_comissao_vendas_detalhada = load_comissao_vendas_detalhada(mydb, cursor, data_inicio, data_fim)
    global_df_metas_unidade_diario = load_comissao_metas_unid_diario(mydb, cursor, data_inicio, data_fim)
    global_df_voucher_wordpress = load_vouchers_wordpress(mydb, cursor, data_inicio, data_fim)
    global_df_metas_unidade_diario_vendas_acumulado = load_meta_unidade_vendas_acumulado(mydb, cursor, data_inicio, data_fim)
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

def load_resumo_vendas(mydb, cursor, data_inicio, data_fim):
    if not cursor:
        return pd.DataFrame()
    
    sqlQuery = """
        SELECT * 
        FROM vw_resumo_vendas_por_origem t
        WHERE t.lancamento BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    #desconectarDB(mydb, cursor)
    return df


def load_comissao_prof_tecnicas(mydb, cursor, data_inicio, data_fim):
    if not cursor:
        return pd.DataFrame()
    
    sqlQuery = """
        SELECT * 
        FROM comissao_prof_tecnicas_detalhada t
        WHERE t.data BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    #desconectarDB(mydb, cursor)
    return df

def load_comissao_vendas_detalhada(mydb, cursor, data_inicio, data_fim):
    if not cursor:
        return pd.DataFrame()
    
    sqlQuery = """
        SELECT * 
        FROM comissao_vendas_detalhada t
        WHERE t.data BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    #desconectarDB(mydb, cursor)
    return df

def load_comissao_metas_unid_diario(mydb, cursor, data_inicio, data_fim):
    if not cursor:
        return pd.DataFrame()
    
    sqlQuery = """
        SELECT * 
        FROM metas_vendas_unidade_diario t
        WHERE t.data BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    #desconectarDB(mydb, cursor)
    return df

def load_vouchers_wordpress(mydb, cursor, data_inicio, data_fim):
    return load_generico("vouchers_wordpress", "data_utilizacao", mydb, cursor, data_inicio, data_fim)

def load_meta_unidade_vendas_acumulado(mydb, cursor, data_inicio, data_fim):
    global global_df_metas_unidade_diario_vendas_acumulado

    df = load_generico("view_metas_vs_vendas", "data", mydb, cursor, data_inicio, data_fim)
    df["delta"] = df["valor_vendido"] - df["meta_total_ajustado"]

    linha_total = pd.DataFrame([{
                        "data": "",
                        "meta_total_ajustado": df["meta_total_ajustado"].sum(),
                        "delta": df["delta"].sum(),
                        "valor_vendido": df["valor_vendido"].sum()
                    }])
    retorno = pd.concat([df, linha_total], ignore_index=True)

    return retorno

def faturamento():
    global global_df_resumo_vendas

    total = global_df_resumo_vendas["total_geral"].sum()
    return total

def faturamento_detalhado():
    global global_df_resumo_vendas

    retorno = global_df_resumo_vendas[["total_geral", "total_plano", "total_voucher", "total_servico", "total_produto", "total_outros"]].sum().to_frame().T
    return retorno

def faturamento_meta_acumulada_diario():
    global global_df_metas_unidade_diario_vendas_acumulado
    return global_df_metas_unidade_diario_vendas_acumulado

def num_atendimentos():
    global global_df_comissao_prof_tecnicas

    df_filtrado = global_df_comissao_prof_tecnicas[~global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]
    retorno = df_filtrado["id_atendimento"].nunique()
    return retorno

def num_clientes_unicos():
    global global_df_comissao_prof_tecnicas

    retorno = global_df_comissao_prof_tecnicas["cliente"].nunique()
    return retorno

def num_atendimentos_banho():
    global global_df_comissao_prof_tecnicas

    df_filtrado = global_df_comissao_prof_tecnicas[global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]
    retorno = df_filtrado["id_atendimento"].nunique()
    return retorno

def atendimentos_tempo_medio():
    global global_df_comissao_prof_tecnicas
    df_filtrado = global_df_comissao_prof_tecnicas[~global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]
    
    # Extração robusta do tempo (mesmo se vier antes de palavras como 'Dom')
    df_filtrado['tempo_min'] = df_filtrado['servico'].str.extract(r'(\d{2,3})(?!\S)', expand=False)

    # Substitui valores ausentes por 0 e converte para inteiro
    df_filtrado['tempo_min'] = df_filtrado['tempo_min'].fillna(0).astype(int)

    tempo_total = df_filtrado['tempo_min'].sum()

    return round(tempo_total / len(df_filtrado), 2) if len(df_filtrado) > 0 else 0.0

def terapeutas_reparticao():
    global global_df_comissao_prof_tecnicas
    
    df_filtrado = global_df_comissao_prof_tecnicas[~global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]

    agrupado = df_filtrado.groupby("profissional").agg(
        reparticao=("comissao_valor", "sum"),
        clientes_unicos=("cliente", "nunique"),
        atendimentos=("id_atendimento", "count"),
        dias_atendimento=("data", "nunique"),
        atendimentos_unicos=("id_atendimento", "nunique")
    ).reset_index()
    agrupado["media_atend_dia"] = agrupado["atendimentos"] / agrupado["dias_atendimento"]
    agrupado["media_atend_dia"] = agrupado["atendimentos"].div(agrupado["dias_atendimento"].replace(0, pd.NA))

    linha_total = pd.DataFrame([{
                        "profissional": "TOTAL",
                        "reparticao": agrupado["reparticao"].sum(),
                        "atendimentos": agrupado["atendimentos"].sum(),
                        "atendimentos_unicos": agrupado["atendimentos_unicos"].sum()
                    }])
    retorno = pd.concat([agrupado, linha_total], ignore_index=True)

    return retorno

def terapia_media_por_atendimento():
    global global_df_comissao_prof_tecnicas
    
    df_filtrado = global_df_comissao_prof_tecnicas[~global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]
    agrupado = df_filtrado.groupby("id_atendimento").agg(
        reparticao=("comissao_valor", "sum"),
        servicos_atendidos=("servico", "nunique")
    ).reset_index()
    
    return agrupado["servicos_atendidos"].mean()

def reparticao_media_por_atendimento():
    global global_df_comissao_prof_tecnicas
    
    df_filtrado = global_df_comissao_prof_tecnicas[~global_df_comissao_prof_tecnicas['profissional'].str.contains('banho', case=False, na=False)]
    agrupado = df_filtrado.groupby("id_atendimento").agg(
        reparticao=("comissao_valor", "sum"),
        servicos_atendidos=("servico", "nunique")
    ).reset_index()
    
    return agrupado["reparticao"].mean()

def faturamento_voucher_online():
    global global_df_voucher_wordpress

    total = global_df_voucher_wordpress["valor_reembolso"].sum()
    return total

def faturamento_meta():
    global global_df_metas_unidade_diario

    # Converter coluna para datetime
    global_df_metas_unidade_diario["data"] = pd.to_datetime(global_df_metas_unidade_diario["data"], format="%Y-%m-%d", errors="coerce")
    # Data de hoje
    hoje = pd.Timestamp(date.today())
    
    # Filtrar datas menores ou iguais a hoje
    df_filtrado = global_df_metas_unidade_diario[global_df_metas_unidade_diario["data"] <= hoje]
    retorno = df_filtrado["meta_total_ajustado"].sum()
    return retorno

def faturamento_meta_do_dia():
    global global_df_metas_unidade_diario

    # Converter coluna para datetime
    global_df_metas_unidade_diario["data"] = pd.to_datetime(global_df_metas_unidade_diario["data"], format="%Y-%m-%d", errors="coerce")
    # Data de hoje
    hoje = pd.Timestamp(date.today())
    
    # Filtrar datas menores ou iguais a hoje
    df_filtrado = global_df_metas_unidade_diario[global_df_metas_unidade_diario["data"] == hoje]
    retorno = df_filtrado["meta_total_ajustado"].sum()
    return retorno

def voucher_wordpress_meta():
    global global_df_metas_unidade_diario

    # Converter coluna para datetime
    global_df_metas_unidade_diario["data"] = pd.to_datetime(global_df_metas_unidade_diario["data"], format="%Y-%m-%d", errors="coerce")
    # Data de hoje
    hoje = pd.Timestamp(date.today())
    
    # Filtrar datas menores ou iguais a hoje
    df_filtrado = global_df_metas_unidade_diario[global_df_metas_unidade_diario["data"] <= hoje]
    retorno = df_filtrado["meta_voucher_online"].sum()
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