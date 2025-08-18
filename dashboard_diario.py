import streamlit as st
import pandas as pd
from datetime import date, timedelta
import dashboard_diario_indicadores as dIndicadores


def DashDiario(unidade, dbUser, dbDataBase):
    st.set_page_config(layout="wide")
    #st.set_page_config(layout="centered")

    unidadeDesc = ""
    if unidade == "GoldenSquare":
        unidadeDesc = "Golden Square"
    elif unidade == "PartageSantana":
        unidadeDesc = "Partage Santana"
    
    dIndicadores.database(dbUser, dbDataBase)

    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout"):
            for key in ["logado", "usuario", "pagina_destino", "unidade", "dbUser", "dbDataBase"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


    # Título e seleção de data
    st.title("🗕️ Dashboard Diário - " + unidadeDesc)
    st.markdown("Selecione a data de referência para análise")
    data_ref = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    data_ref_menos_7 = data_ref - timedelta(days=7)


    # Produtos, Vouchers e Pacotes
    resumo = dIndicadores.resumo_vendas_por_origem(data_ref)
    resumo_menos_7 = dIndicadores.resumo_vendas_por_origem(data_ref_menos_7)

    if resumo is not None and not resumo.empty:
        row = resumo.iloc[0]

        produtos_qtd = row['qtd_vendas_produto']
        produtos_faturamento = dIndicadores.formatar_reais(row['total_produto'])
        produtos_ticket = dIndicadores.formatar_reais(row['ticket_medio_produto'])

        vouchers_qtd = row['qtd_vendas_voucher']
        vouchers_faturamento = dIndicadores.formatar_reais(row['total_voucher'])
        vouchers_ticket = dIndicadores.formatar_reais(row['ticket_medio_voucher'])

        pacotes_qtd = row['qtd_vendas_plano']
        pacotes_faturamento = dIndicadores.formatar_reais(row['total_plano'])
        pacotes_ticket = dIndicadores.formatar_reais(row['ticket_medio_plano'])

        servicos_qtd = row['qtd_vendas_servico']
        servicos_faturamento = dIndicadores.formatar_reais(row['total_servico'])
        servicos_ticket = dIndicadores.formatar_reais(row['ticket_medio_servico'])
        servicos_qtde_atend_voucher = row['atendimentos_voucher']
        servicos_financeiro_atend_voucher = row['total_financeiro_voucher_atendido']
    else:
        # Fallback padrão (tudo zero ou vazio)
        produtos_qtd = vouchers_qtd = pacotes_qtd = servicos_qtd = 0

        produtos_faturamento = produtos_ticket = dIndicadores.formatar_reais(0)
        vouchers_faturamento = vouchers_ticket = dIndicadores.formatar_reais(0)
        pacotes_faturamento = pacotes_ticket = dIndicadores.formatar_reais(0)
        servicos_faturamento = servicos_ticket = dIndicadores.formatar_reais(0)
        
        servicos_qtde_atend_voucher = servicos_financeiro_atend_voucher = 0

    if resumo_menos_7 is not None and not resumo_menos_7.empty:
        row = resumo_menos_7.iloc[0]
        servicos_qtde_atend_voucher_menos_7 = row['atendimentos_voucher']
    else:
        servicos_qtde_atend_voucher_menos_7 = 0
        

    st.divider()

    # --- Atendimento ---
    st.subheader("📋 Atendimento")
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)
    col9, col10, col11, col12 = st.columns(4)

    total_agendado = dIndicadores.total_agendado(data_ref, data_ref)
    total_agendado_menos_7 = dIndicadores.total_agendado(data_ref_menos_7, data_ref_menos_7)
    agendado_delta = total_agendado - total_agendado_menos_7

    total_atendido = dIndicadores.total_atendido(data_ref, data_ref)
    atendido_delta = total_atendido - dIndicadores.total_atendido(data_ref_menos_7, data_ref_menos_7)

    wellhub = dIndicadores.atendimentos_Wellhub(data_ref, data_ref)
    wellhub_delta = wellhub - dIndicadores.atendimentos_Wellhub(data_ref_menos_7, data_ref_menos_7)

    totalpass = dIndicadores.atendimentos_totalpass(data_ref, data_ref)
    totalpass_delta = totalpass - dIndicadores.atendimentos_totalpass(data_ref_menos_7, data_ref_menos_7)

    numero_terapeutas = dIndicadores.total_terapeutas(data_ref, data_ref)
    numero_terapeutas_menos_7 = dIndicadores.total_terapeutas(data_ref_menos_7, data_ref_menos_7)
    terapeutas_delta = numero_terapeutas - numero_terapeutas_menos_7

    no_show = dIndicadores.total_noshow(data_ref, data_ref)
    no_show_menos_7 = dIndicadores.total_noshow(data_ref_menos_7, data_ref_menos_7)
    no_show_delta = (no_show - no_show_menos_7)*-1

    tMed = dIndicadores.tempo_medio_terapias(data_ref, data_ref)
    tempo_medio = str(tMed) + ' min'
    tempo_medio_delta = str(round(tMed - dIndicadores.tempo_medio_terapias(data_ref_menos_7, data_ref_menos_7),2)) + ' min'

    atend_por_terapeuta = round(total_atendido / numero_terapeutas, 2) if numero_terapeutas > 0 else 0
    atend_terapeuta_delta = (
        round(atend_por_terapeuta - (total_agendado_menos_7 / numero_terapeutas_menos_7), 2)
        if numero_terapeutas_menos_7 > 0 else 0
    )


    terapia_por_atendimento = dIndicadores.media_terapias_atendimento(data_ref, data_ref)
    terapia_por_atendimento_menos_7 = dIndicadores.media_terapias_atendimento(data_ref_menos_7, data_ref_menos_7)
    terapia_delta = round(terapia_por_atendimento - terapia_por_atendimento_menos_7, 2)

    numero_banhos = dIndicadores.numero_banhos(data_ref, data_ref)
    numero_banhos_menos_7 = dIndicadores.numero_banhos(data_ref_menos_7, data_ref_menos_7)
    numero_banhos_delta = numero_banhos - numero_banhos_menos_7

    atendimentos_voucher_delta = int(servicos_qtde_atend_voucher - servicos_qtde_atend_voucher_menos_7)

    with col1:
        st.metric("Total Agendado", total_agendado, delta=int(agendado_delta))
    with col2:
        st.metric("Total Atendido", total_atendido, delta=atendido_delta)
    with col3:
        st.metric("Atendimentos Voucher", servicos_qtde_atend_voucher, delta=atendimentos_voucher_delta)
    with col4:
        st.metric("No-show", no_show, delta=int(no_show_delta))
        

    with col5:
        st.metric("Tempo Médio Atendimento", tempo_medio, delta=tempo_medio_delta)
    with col6:
        st.metric("Terapia por atendimento", terapia_por_atendimento, delta=terapia_delta)
    with col7:
        st.metric("Número Terapeutas", numero_terapeutas, delta=terapeutas_delta)
    with col8:
        st.metric("Atend/terapeuta", atend_por_terapeuta, delta=atend_terapeuta_delta)

    with col9:
        st.metric("Número Banhos", numero_banhos, delta=numero_banhos_delta)
    with col10:
        st.metric("Totalpass", totalpass, delta=totalpass_delta)
    with col11:
        st.metric("Wellhub", wellhub, delta=wellhub_delta)

    st.divider()

    # --- Financeiro ---
    st.subheader("💰 Financeiro")
    cfXpto, cfx2 = st.columns(2)

    cf1, cf2, cf3, cf4 = st.columns(4)


    faturamento_dia = (dIndicadores.faturamento(data_ref, data_ref)) #"R$ 2.500"
    faturamento_dia_menos_7 = dIndicadores.faturamento(data_ref_menos_7, data_ref_menos_7)
    faturamento_delta = faturamento_dia - faturamento_dia_menos_7#"R$ 300"

    debito = dIndicadores.faturamento_debito(data_ref, data_ref)
    debito_menos_7 = dIndicadores.faturamento_debito(data_ref_menos_7, data_ref_menos_7)
    debito_delta = debito - debito_menos_7

    pix = dIndicadores.faturamento_pix(data_ref, data_ref)
    pix_menos_7 = dIndicadores.faturamento_pix(data_ref_menos_7, data_ref_menos_7)
    pix_delta = pix - pix_menos_7

    credito = dIndicadores.faturamento_credito(data_ref, data_ref)
    credito_menos_7 = dIndicadores.faturamento_credito(data_ref_menos_7, data_ref_menos_7)
    credito_delta = credito - credito_menos_7

    dinheiro = dIndicadores.faturamento_dinheiro(data_ref, data_ref)
    dinheiro_menos_7 = dIndicadores.faturamento_dinheiro(data_ref_menos_7, data_ref_menos_7)
    dinheiro_delta = dinheiro - dinheiro_menos_7


    with cfXpto:
        st.markdown(f"""
        <div style='font-size: 20px; font-weight: bold'>Faturamento Dia</div>
        <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(faturamento_dia)}</div>
        <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(faturamento_delta)}</div><br>
        """, unsafe_allow_html=True)

    with cf1:
        st.markdown(f"""
        <div style='font-size: 20px; font-weight: bold'>💳 Débito</div>
        <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(debito)}</div>
        <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(debito_delta)}</div>
        """, unsafe_allow_html=True)

    with cf2:
        st.markdown(f"""
        <div style='font-size: 20px; font-weight: bold'>⚡ Pix</div>
        <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(pix)}</div>
        <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(pix_delta)}</div>
        """, unsafe_allow_html=True)

    with cf3:
        st.markdown(f"""
        <div style='font-size: 20px; font-weight: bold'>💳 Crédito</div>
        <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(credito)}</div>
        <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(credito_delta)}</div>
        """, unsafe_allow_html=True)

    with cf4:
        st.markdown(f"""
        <div style='font-size: 20px; font-weight: bold'>💵 Dinheiro</div>
        <div style='font-size: 24px; color: black'>{dIndicadores.formatar_reais(dinheiro)}</div>
        <div style='font-size: 14px; color: gray'>Delta: {dIndicadores.formatar_reais(dinheiro_delta)}</div><br><br>
        """, unsafe_allow_html=True)



    # Produtos, Vouchers e Pacotes


    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown("### Produtos")
        st.markdown(f"Quantidade: **{produtos_qtd}**")
        st.markdown(f"Faturamento: **{produtos_faturamento}**")
        st.markdown(f"Ticket Médio: **{produtos_ticket}**")

    with p2:
        st.markdown("### Vouchers")
        st.markdown(f"Quantidade: **{vouchers_qtd}**")
        st.markdown(f"Faturamento: **{vouchers_faturamento}**")
        st.markdown(f"Ticket Médio: **{vouchers_ticket}**")

    with p3:
        st.markdown("### Pacotes")
        st.markdown(f"Quantidade: **{pacotes_qtd}**")
        st.markdown(f"Faturamento: **{pacotes_faturamento}**")
        st.markdown(f"Ticket Médio: **{pacotes_ticket}**")

    with p4:
        st.markdown("### Serviços")
        st.markdown(f"Quantidade: **{servicos_qtd}**")
        st.markdown(f"Faturamento: **{servicos_faturamento}**")
        st.markdown(f"Ticket Médio: **{servicos_ticket}**")
        st.markdown(f"Qtde Voucher: **{servicos_qtde_atend_voucher}**")
        st.markdown(f"R$ Voucher: **{servicos_financeiro_atend_voucher}**")

    st.divider()

    st.dataframe(dIndicadores.pagamentos_dia(data_ref, data_ref))

    st.divider()

    # --- Avaliação NPS ---

    #st.subheader("🌟 Avaliação NPS")
    nps1, nps2, nps3, nps4 = st.columns(4)

    pesquisas_respondidas = 50
    pesquisas_delta = 10

    promotores = 30
    promotores_delta = 5

    neutros = 10
    neutros_delta = -2

    detratores = 10
    detratores_delta = 1

    nps_terapeuta = "75"
    nps_terapeuta_delta = 10

    nps_atendimento = "68"
    nps_atendimento_delta = 5

    #with nps1:
    #    st.metric("Pesquisas Respondidas", pesquisas_respondidas, delta=pesquisas_delta)
    #with nps2:
    #    st.metric("Promotores", promotores, delta=promotores_delta)
    #with nps3:
    #    st.metric("Neutros", neutros, delta=neutros_delta)
    #with nps4:
    #    st.metric("Detratores", detratores, delta=detratores_delta)

    nps5, nps6 = st.columns(2)
    #with nps5:
    #    st.metric("NPS Terapeuta", nps_terapeuta, delta=nps_terapeuta_delta)
    #with nps6:
    #    st.metric("NPS Atendimento", nps_atendimento, delta=nps_atendimento_delta)
