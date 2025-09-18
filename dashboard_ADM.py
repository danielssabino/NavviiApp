import streamlit as st
import pandas as pd
from datetime import date, timedelta
import dashboard_ADM_indicadores as dIndicadores
import calendar

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_inteiro(valor):
    return f"{valor:,}".replace(",", ".")

def formatar_decimal(valor):
    if pd.isna(valor):  # evita erro com NaN
        return "-"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def DashDiarioADM(unidade, dbUser, dbDataBase):
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


    # 📌 Descobre primeiro e último dia do mês atual
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    

    # Título e seleção de data
    st.title("🗕️ Dashboard ADM - " + unidadeDesc)
    st.markdown("Selecione a data de referência para análise")
    
    # 📌 Seletor de intervalo de datas com valores padrão
    col1, col2, col3 = st.columns([1,2,1])

    with col3:
        data_inicio, data_fim = st.date_input(
            "Selecione o período:",
            value=(primeiro_dia, ultimo_dia),
            format="DD/MM/YYYY"
        )
    
    
    # data_inicio, data_fim = st.date_input(
    #     "Selecione o período:",
    #     value=(primeiro_dia, ultimo_dia), format="DD/MM/YYYY"
    # )

    dIndicadores.LoadData(dbUser, dbDataBase,data_inicio, data_fim)
    
    #data_ref = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    #data_ref_menos_7 = data_ref - timedelta(days=7)

    faturamento = dIndicadores.faturamento()
    faturamento_detalhado = dIndicadores.faturamento_detalhado()

    faturmento_voucher_online = dIndicadores.faturamento_voucher_online()

    faturamento_mata = dIndicadores.faturamento_meta()
    faturmento_voucher_online_meta = dIndicadores.voucher_wordpress_meta()
    faturamento_meta_acumulada = dIndicadores.faturamento_meta_acumulada_diario()

    atendimentos_totais = dIndicadores.num_atendimentos()
    atendimentos_clientes_unicos = dIndicadores.num_clientes_unicos()
    atendimentos_banho = dIndicadores.num_atendimentos_banho()
    atendimentos_tempo_medio = dIndicadores.atendimentos_tempo_medio()
    terapia_media_por_atendimento = dIndicadores.terapia_media_por_atendimento()
    reparticao_media_por_atendimento = dIndicadores.reparticao_media_por_atendimento()

    teapeutas_reparticao = dIndicadores.terapeutas_reparticao()
    
    st.divider()

    # # --- Atendimento ---
    st.subheader("💰 Financeiro")
    col1, col2, col3 = st.columns(3)
    col4 = st.columns(1)[0]
    colB4 = st.columns(1)[0]
    
    st.subheader("📋 Atendimento")
    col5, col6, col7 = st.columns(3)
    col9, col10, col11 = st.columns(3)

    colB8 = st.columns(1)[0]

    
    with col1:
        cDelta = float(faturamento-faturamento_mata)
        cDelta_color = "normal"
        if (cDelta < 0):
            cDelta_color = "inverse"
        st.metric("Vendas Locais", formatar_moeda(faturamento), delta=formatar_moeda(float(cDelta)), delta_color=cDelta_color)
    with col2:
        cDelta = float(faturmento_voucher_online-faturmento_voucher_online_meta)
        cDelta_color = "normal"
        if (cDelta < 0):
            cDelta_color = "inverse"
        st.metric("Voucher Online", formatar_moeda(faturmento_voucher_online), delta=formatar_moeda(cDelta), delta_color=cDelta_color)
    with col3:
        cDelta = float((faturamento+faturmento_voucher_online)-(faturamento_mata+faturmento_voucher_online_meta))
        cDelta_color = "normal"
        if (cDelta < 0):
            cDelta_color = "inverse"
        st.metric("Faturamento Total", formatar_moeda(faturamento+faturmento_voucher_online), delta=formatar_moeda(cDelta), delta_color=cDelta_color)
    
    with col4:
       
        # Aplicar estilo de formatação
        df = faturamento_detalhado[["total_plano", "total_produto", "total_voucher", "total_servico", "total_outros"]].rename(columns={
                "total_geral": "Vendas Locais",
                "total_plano": "Planos",
                "total_voucher": "Vouchers",
                "total_servico": "Serviços",
                "total_produto": "Produtos",
                "total_outros": "Outros",
            })  
        # Formatando no padrão brasileiro
        styled_df = df.style.format({
            "Planos": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Vouchers": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),       # sem decimal
            "Serviços": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),       # sem decimal
            "Produtos": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Outros": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")        # sem decimal
        })
        st.dataframe(styled_df, use_container_width=True)
        
        #st.write(faturamento_detalhado)
    with colB4:
         # Converter string -> datetime
        #faturamento_meta_acumulada["data"] = pd.to_datetime(faturamento_meta_acumulada["data"], errors="coerce")

        faturamento_meta_acumulada["data"] = pd.to_datetime(faturamento_meta_acumulada["data"], errors="coerce")
        # 2) Formata para dd/mm/yyyy, tratando NaT
        faturamento_meta_acumulada["data_formatada"] = faturamento_meta_acumulada["data"].dt.strftime("%d/%m/%Y").fillna("-")

        df = faturamento_meta_acumulada[["data_formatada", "meta_total_ajustado", "valor_vendido", "meta_acumulada", "valor_vendido_acumulado", "delta"]].rename(columns={
                "data_formatada": "Data",
                "meta_total_ajustado": "Meta Planejada",
                "valor_vendido": "Valor Vendido",
                "meta_acumulada": "Meta Acumulada",
                "valor_vendido_acumulado": "Valor Vendido Acumulado",
                "delta": "Diferença Meta x Vendas",
            })

        # Formatando no padrão brasileiro
        styled_df = df.style.format({
            #"Data": lambda x: "-" if pd.isna(x) else x.strftime("%d/%m/%Y"),
            "Meta Planejada": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Valor Vendido": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),       # sem decimal
            "Valor Vendido": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),       # sem decimal
            "Meta Acumulada": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Valor Vendido Acumulado": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Diferença Meta x Vendas": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")        # sem decimal
        })
        st.dataframe(styled_df, use_container_width=True)

    with col5:
        st.metric("Total Atendimentos", atendimentos_totais)
    with col6:
        st.metric("Clientes Únicos", atendimentos_clientes_unicos)
    with col7:
        st.metric("Qtde. Banhos", atendimentos_banho)
    #with col8:
        
    
    with col9:
        st.metric("Tempo Méd. Atendimento", formatar_decimal(atendimentos_tempo_medio))
    with col10:
        st.metric("Terapia Méd. Atendimento", formatar_decimal(terapia_media_por_atendimento))
    with col11:
        st.metric("Repartição Méd. Atendimento", formatar_moeda(reparticao_media_por_atendimento))

    with colB8:
        # Aplicar estilo de formatação
        df = teapeutas_reparticao.rename(columns={
                "profissional": "Profissional",
                "reparticao": "Repartição",
                "clientes_unicos": "Clientes Únicos",
                "atendimentos": "Atendimentos",
                "atendimentos_unicos": "Atendimentos Únicos",
                "dias_atendimento": "Dias Atendimento",
                "media_atend_dia": "Média Atendimentos Dia"
                
            })
        # Formatando no padrão brasileiro
        styled_df = df.style.format({
            "Repartição": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Clientes Únicos": "{:,.0f}" ,       # sem decimal
            "Atendimentos": "{:,.0f}" ,       # sem decimal
            "Dias Atendimento": "{:,.0f}" ,       # sem decimal
            "Média Atendimentos Dia": "{:,.2f}" ,       # 2 decimais
            "Atendimentos Únicos": "{:,.0f}"        # sem decimal
        })
        st.dataframe(styled_df, use_container_width=True)




    st.divider()

    # # --- Financeiro ---
    # st.subheader("💰 Financeiro")
    # cfXpto, cfx2 = st.columns(2)

    # cf1, cf2, cf3, cf4 = st.columns(4)


    # faturamento_dia = (dIndicadores.faturamento(data_ref, data_ref)) #"R$ 2.500"
    # faturamento_dia_menos_7 = dIndicadores.faturamento(data_ref_menos_7, data_ref_menos_7)
    # faturamento_delta = faturamento_dia - faturamento_dia_menos_7#"R$ 300"

    # debito = dIndicadores.faturamento_debito(data_ref, data_ref)
    # debito_menos_7 = dIndicadores.faturamento_debito(data_ref_menos_7, data_ref_menos_7)
    # debito_delta = debito - debito_menos_7

    # pix = dIndicadores.faturamento_pix(data_ref, data_ref)
    # pix_menos_7 = dIndicadores.faturamento_pix(data_ref_menos_7, data_ref_menos_7)
    # pix_delta = pix - pix_menos_7

    # credito = dIndicadores.faturamento_credito(data_ref, data_ref)
    # credito_menos_7 = dIndicadores.faturamento_credito(data_ref_menos_7, data_ref_menos_7)
    # credito_delta = credito - credito_menos_7

    # dinheiro = dIndicadores.faturamento_dinheiro(data_ref, data_ref)
    # dinheiro_menos_7 = dIndicadores.faturamento_dinheiro(data_ref_menos_7, data_ref_menos_7)
    # dinheiro_delta = dinheiro - dinheiro_menos_7


    # with cfXpto:
    #     st.markdown(f"""
    #     <div style='font-size: 20px; font-weight: bold'>Faturamento Dia</div>
    #     <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(faturamento_dia)}</div>
    #     <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(faturamento_delta)}</div><br>
    #     """, unsafe_allow_html=True)

    # with cf1:
    #     st.markdown(f"""
    #     <div style='font-size: 20px; font-weight: bold'>💳 Débito</div>
    #     <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(debito)}</div>
    #     <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(debito_delta)}</div>
    #     """, unsafe_allow_html=True)

    # with cf2:
    #     st.markdown(f"""
    #     <div style='font-size: 20px; font-weight: bold'>⚡ Pix</div>
    #     <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(pix)}</div>
    #     <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(pix_delta)}</div>
    #     """, unsafe_allow_html=True)

    # with cf3:
    #     st.markdown(f"""
    #     <div style='font-size: 20px; font-weight: bold'>💳 Crédito</div>
    #     <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(credito)}</div>
    #     <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(credito_delta)}</div>
    #     """, unsafe_allow_html=True)

    # with cf4:
    #     st.markdown(f"""
    #     <div style='font-size: 20px; font-weight: bold'>💵 Dinheiro</div>
    #     <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(dinheiro)}</div>
    #     <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(dinheiro_delta)}</div><br><br>
    #     """, unsafe_allow_html=True)



    # # Produtos, Vouchers e Pacotes


    # p1, p2, p3, p4 = st.columns(4)

    # with p1:
    #     st.markdown("### Produtos")
    #     st.markdown(f"Quantidade: **{produtos_qtd}**")
    #     st.markdown(f"Faturamento: **{produtos_faturamento}**")
    #     st.markdown(f"Ticket Médio: **{produtos_ticket}**")

    # with p2:
    #     st.markdown("### Vouchers")
    #     st.markdown(f"Quantidade: **{vouchers_qtd}**")
    #     st.markdown(f"Faturamento: **{vouchers_faturamento}**")
    #     st.markdown(f"Ticket Médio: **{vouchers_ticket}**")

    # with p3:
    #     st.markdown("### Pacotes")
    #     st.markdown(f"Quantidade: **{pacotes_qtd}**")
    #     st.markdown(f"Faturamento: **{pacotes_faturamento}**")
    #     st.markdown(f"Ticket Médio: **{pacotes_ticket}**")

    # with p4:
    #     st.markdown("### Serviços")
    #     st.markdown(f"Quantidade: **{servicos_qtd}**")
    #     st.markdown(f"Faturamento: **{servicos_faturamento}**")
    #     st.markdown(f"Ticket Médio: **{servicos_ticket}**")
    #     st.markdown(f"Qtde Voucher: **{servicos_qtde_atend_voucher}**")
    #     st.markdown(f"R$ Voucher: **{servicos_financeiro_atend_voucher}**")

    # st.divider()

    # st.dataframe(dIndicadores.pagamentos_dia(data_ref, data_ref))

    # st.divider()

    # # --- Avaliação NPS ---

    # #st.subheader("🌟 Avaliação NPS")
    # nps1, nps2, nps3, nps4 = st.columns(4)

    # pesquisas_respondidas = 50
    # pesquisas_delta = 10

    # promotores = 30
    # promotores_delta = 5

    # neutros = 10
    # neutros_delta = -2

    # # detratores = 10
    # # detratores_delta = 1

    # # nps_terapeuta = "75"
    # # nps_terapeuta_delta = 10

    # # nps_atendimento = "68"
    # # nps_atendimento_delta = 5

    # #with nps1:
    # #    st.metric("Pesquisas Respondidas", pesquisas_respondidas, delta=pesquisas_delta)
    # #with nps2:
    # #    st.metric("Promotores", promotores, delta=promotores_delta)
    # #with nps3:
    # #    st.metric("Neutros", neutros, delta=neutros_delta)
    # #with nps4:
    # #    st.metric("Detratores", detratores, delta=detratores_delta)

    # nps5, nps6 = st.columns(2)
    # #with nps5:
    # #    st.metric("NPS Terapeuta", nps_terapeuta, delta=nps_terapeuta_delta)
    # #with nps6:
    # #    st.metric("NPS Atendimento", nps_atendimento, delta=nps_atendimento_delta)
