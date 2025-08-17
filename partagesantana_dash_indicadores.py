import mysql.connector as conn
import pandas as pd
from datetime import date


def conectarDB():
    try:
        mydb = conn.connect(
            host="dboperacaobda.mysql.uhserver.com",
            user="usroperacaobda", #usrgoldensquare       -usroperacaobda
            password="i96d1e8zq9@",
            database="dboperacaobda" #dbgoldensquare     - dboperacaobda
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

#========= atendimentos ===================
def buscar_atendimentos(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM atendimentos atend
        WHERE atend.data BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df


def buscar_atend_terapeutas(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM comissao_prof_tecnicas_detalhada a
        WHERE a.data BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df


def buscar_parcerias(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM demonstrativo_vendas_detalhado vendas
        INNER JOIN demonstrativo_vendas_detalhado_pgto pgto ON vendas.id_venda = pgto.id_venda
        WHERE pgto.forma_pagamento LIKE 'Parcerias Comerciais%'
        AND vendas.lancamento BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df

# Função para contar quantos serviços existem em cada linha
def contar_servicos(texto):
    if pd.isna(texto):
        return 0
    return max(1, texto.count(',') + 1 if '-' in texto else 1)

def total_agendado(data_inicio, data_fim):
    #print (data_inicio)
    #print (data_fim)
    df = buscar_atendimentos(data_inicio, data_fim)
    df['qtd_servicos'] = df['servico'].apply(contar_servicos)
    #print(df)
    df_filtrado = df[~df['profissional'].str.contains('banho', case=False, na=False)]
    #print(df_filtrado)
    total_servicos = df_filtrado['qtd_servicos'].sum()

    return total_servicos

def total_noshow(data_inicio, data_fim):
    #print (data_inicio)
    #print (data_fim)
    df = buscar_atendimentos(data_inicio, data_fim)
    df['qtd_servicos'] = df['servico'].apply(contar_servicos)
    #print(df)
    df_filtrado = df[df['status'].str.lower().isin(['cancelado', 'desmarcado'])]
    #print(df_filtrado)
    total_servicos = df_filtrado['qtd_servicos'].sum()

    return total_servicos


def total_atendido(data_inicio, data_fim):
    
    df = buscar_atend_terapeutas(data_inicio, data_fim)
    df_filtrado = df[~df['profissional'].str.contains('banho', case=False, na=False)]
    return len(df_filtrado)


def total_terapeutas(data_inicio, data_fim):
    df = buscar_atend_terapeutas(data_inicio, data_fim)
    df_filtrado = df[~df['profissional'].str.contains('banho', case=False, na=False)]
    return df_filtrado['profissional'].nunique() if 'profissional' in df.columns else 0


def atendimentos_totalpass(data_inicio, data_fim):
    df = buscar_parcerias(data_inicio, data_fim)
    filtered = df[df['forma_pagamento'].str.contains('TotalPass', case=False, na=False)]
    return len(filtered)


def atendimentos_Wellhub(data_inicio, data_fim):
    df = buscar_parcerias(data_inicio, data_fim)
    filtered = df[df['forma_pagamento'].str.contains('Gympass', case=False, na=False)]
    return len(filtered)

def tempo_medio_terapias(data_inicio, data_fim):
    df = buscar_atend_terapeutas(data_inicio, data_fim)
    
    if df.empty or 'servico' not in df.columns:
        return 0.0  # Ou None, dependendo de como você quer tratar

    # Extração robusta do tempo (mesmo se vier antes de palavras como 'Dom')
    df['tempo_min'] = df['servico'].str.extract(r'(\d{2,3})(?!\S)', expand=False)

    # Substitui valores ausentes por 0 e converte para inteiro
    df['tempo_min'] = df['tempo_min'].fillna(0).astype(int)

    tempo_total = df['tempo_min'].sum()

    return round(tempo_total / len(df), 2) if len(df) > 0 else 0.0

def media_terapias_atendimento(data_inicio, data_fim):
    df = buscar_atend_terapeutas(data_inicio, data_fim)
    # Conta o número total de terapias (linhas)
    total_terapias = len(df)
    # Conta o número de atendimentos distintos
    total_atendimentos = df['id_atendimento'].nunique()
    #df_filtrado = df[~df['profissional'].str.contains('banho', case=False, na=False)]

    # Calcula a média
    media_terapias_por_atendimento = (
    round(total_terapias / total_atendimentos, 2)
    if total_atendimentos > 0 else 0
    )

    return media_terapias_por_atendimento

def numero_banhos(data_inicio, data_fim):
    df = buscar_atend_terapeutas(data_inicio, data_fim)
    df_filtrado = df[df['profissional'].str.contains('banho', case=False, na=False)]
    return len(df_filtrado)



#========= financeiro ===================
def demonstrtivo_vendas_detalhado(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM demonstrativo_vendas_detalhado a
        WHERE a.lancamento BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df

def demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT a.*, p.id_parcela, p.parcela, p.forma_pagamento, p.data, p.valor, p.status
        FROM `demonstrativo_vendas_detalhado` a
        inner join demonstrativo_vendas_detalhado_pgto p on a.id_venda = p.id_venda
        WHERE a.lancamento BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df

def resumo_vendas_por_origem(data_inicio):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM vw_resumo_vendas_por_origem a
        WHERE a.lancamento = %s
    """
    cursor.execute(sqlQuery, (data_inicio,))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df

def pagamentos_dia(data_inicio, data_fim):
    
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim).sort_values(by=["lancamento", "forma_pagamento"])
    df = df[["cliente", "cpf", "responsavel", "servico_produto", "valor_bruto", "valor_desconto", "valor_liquido", "forma_pagamento"]]
    
    return df

def faturamento(data_inicio, data_fim):
    #df = demonstrtivo_vendas_detalhado(data_inicio, data_fim)
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim)
    df_filtrado = df[~df['forma_pagamento'].str.contains('Parcerias Comerciais', case=False, na=False)]
    faturamento = df_filtrado["valor"].sum()
    return faturamento


def faturamento_debito(data_inicio, data_fim):
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim)
    df_filtrado = df[df['forma_pagamento'].str.contains('Cartão de Débito', case=False, na=False)]
    print (df_filtrado)
    return df_filtrado["valor"].sum()

def faturamento_pix(data_inicio, data_fim):
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim)
    df_filtrado = df[df['forma_pagamento'].str.contains('PIX', case=False, na=False)]
    print (df_filtrado)
    return df_filtrado["valor"].sum()

def faturamento_credito(data_inicio, data_fim):
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim)
    df_filtrado = df[df['forma_pagamento'].str.contains('Cartão de Crédito', case=False, na=False)]
    print (df_filtrado)
    return df_filtrado["valor"].sum()


def faturamento_dinheiro(data_inicio, data_fim):
    df = demonstrtivo_vendas_detalhado_pgto(data_inicio, data_fim)
    df_filtrado = df[df['forma_pagamento'].str.contains('Dinheiro', case=False, na=False)]
    print (df_filtrado)
    return df_filtrado["valor"].sum()

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

def buscar_dados(data_inicio, data_fim):
    mydb, cursor = conectarDB()
    if not cursor:
        return pd.DataFrame()

    sqlQuery = """
        SELECT * 
        FROM geracao_voucher 
        WHERE data_venda BETWEEN %s AND %s
    """
    cursor.execute(sqlQuery, (data_inicio, data_fim))
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colnames)

    desconectarDB(mydb, cursor)
    return df
