import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

# IDs fictícios de exemplo
GA4_ID = "G-XXXXXXXXXX"
PIXEL_ID = "123456789012345"

st.set_page_config(page_title="Autoavaliação - Buddha Spa Partage Santana", layout="centered")

# Função para inicializar session_state
def init_session():
    if "page" not in st.session_state:
        st.session_state.page = 0
        st.session_state.answers = {}
        st.session_state.name = ""
        st.session_state.tracked_steps = set()
        st.session_state.scripts_loaded = False

init_session()

# Função para disparar eventos GA4 e Pixel

def trigger_tracking_event(event_name, step=None):
    if step is not None:
        script = f"""
        <script>
        gtag('event', '{event_name}', {{'step': {step}}});
        fbq('trackCustom', '{event_name}', {{step: {step}}});
        </script>
        """
    else:
        script = f"""
        <script>
        gtag('event', '{event_name}');
        fbq('trackCustom', '{event_name}');
        </script>
        """
    components.html(script, height=0)

def next_page():
    st.session_state.page += 1
    step = st.session_state.page
    if step not in st.session_state.tracked_steps:
        st.session_state.tracked_steps.add(step)
        trigger_tracking_event("form_step", step=step)

def previous_page():
    st.session_state.page -= 1

pages = []

# Páginas do formulário progressivo

def page_nome():
    st.title("Avaliação de Bem-Estar")
    st.subheader("Como prefere que a gente te chame?")
    nome = st.text_input("Nome completo")

    # Injeta scripts GA4 e Pixel apenas na primeira execução
    if not st.session_state.scripts_loaded:
        components.html(f"""
        <!-- Google Analytics -->
        <script async src='https://www.googletagmanager.com/gtag/js?id={GA4_ID}'></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA4_ID}');
          gtag('event', 'form_start');
        </script>
        <!-- Meta Pixel -->
        <script>
          !function(f,b,e,v,n,t,s)
          {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
          n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
          if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
          n.queue=[];t=b.createElement(e);t.async=!0;
          t.src=v;s=b.getElementsByTagName(e)[0];
          s.parentNode.insertBefore(t,s)}}(window, document,'script',
          'https://connect.facebook.net/en_US/fbevents.js');
          fbq('init', '{PIXEL_ID}');
          fbq('track', 'PageView');
          fbq('trackCustom', 'form_start');
        </script>
        <noscript><img height='1' width='1' style='display:none'
          src='https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1'/></noscript>
        """, height=0)
        st.session_state.scripts_loaded = True

    if nome:
        st.session_state.answers["nome"] = nome
        st.session_state.name = nome.split(" ")[0].capitalize()
        if st.button("Avançar"):
            next_page()

pages.append(page_nome)

def page_cpf():
    st.subheader(f"Perfeito, {st.session_state.name}! Agora, precisamos do seu CPF")
    cpf = st.text_input("CPF")
    if cpf:
        st.session_state.answers["cpf"] = cpf
        if st.button("Avançar"):
            next_page()

pages.append(page_cpf)

def page_data_nasc():
    st.subheader("Qual sua data de nascimento?")
    data = st.date_input("Data de nascimento", format="DD/MM/YYYY")
    if data:
        st.session_state.answers["data_nascimento"] = data.strftime("%d/%m/%Y")
        if st.button("Avançar"):
            next_page()

pages.append(page_data_nasc)

def page_genero():
    st.subheader("Gênero")
    genero = st.radio("Selecione uma opção:", ["Feminino", "Masculino", "Prefiro não informar"], key="genero")
    st.session_state.answers["genero"] = genero
    if genero and st.button("Avançar"):
        next_page()

pages.append(page_genero)

def page_celular():
    st.subheader("Qual seu celular (com WhatsApp)?")
    celular = st.text_input("Celular")
    if celular:
        st.session_state.answers["celular"] = celular
        if st.button("Avançar"):
            next_page()

pages.append(page_celular)

# Perguntas de autoavaliação corrigidas

def pergunta_multiple_choice(key, pergunta, opcoes):
    st.subheader(pergunta)
    resposta = st.multiselect("", opcoes, key=key)
    if resposta:
        st.session_state.answers[key] = resposta
        if st.button("Avançar"):
            next_page()

def pergunta_single_choice(key, pergunta, opcoes):
    st.subheader(pergunta)
    resposta = st.radio("", opcoes, key=key)
    st.session_state.answers[key] = resposta
    if resposta and st.button("Avançar"):
        next_page()

pages.append(lambda: pergunta_multiple_choice("dores", "Você sente algum desconforto físico com frequência?", ["Ombros/pescoço", "Lombar", "Pernas/pés", "Não sinto dores recorrentes"]))
pages.append(lambda: pergunta_single_choice("sensacao_corpo", "Sensacão predominante no corpo:", ["Peso ou inchaço", "Tensão muscular", "Corpo leve, sem queixas principais"]))
pages.append(lambda: pergunta_single_choice("sono", "Como você descreveria seu sono?", ["Durmo bem, acordo descansado(a)", "Tenho dificuldade para dormir", "Durmo, mas acordo cansado(a)", "Sono irregular"]))
pages.append(lambda: pergunta_single_choice("energia", "Energia no dia a dia:", ["Me sinto bem disposto(a)", "Canso com facilidade", "Sinto-me estressado(a)", "Me sinto sem energia"]))
pages.append(lambda: pergunta_single_choice("rotina", "Como você descreveria sua rotina?", ["Corrida e estressante", "Moderada", "Tranquila", "Sedentária"]))
pages.append(lambda: pergunta_single_choice("tempo_livre", "O que você prefere fazer no seu tempo livre?", ["Descansar em silêncio", "Atividades sociais", "Se manter ativo"]))
pages.append(lambda: pergunta_single_choice("ambiente", "Você sente que sua casa é um ambiente…", ["Leve e organizado", "Pesado e bagunçado"]))
pages.append(lambda: pergunta_single_choice("estatica", "Você costuma levar pequenos choques?", ["Sim", "Não"]))
pages.append(lambda: pergunta_single_choice("objetivo", "O que gostaria de melhorar primeiro?", ["Reduzir dores/tensões", "Melhorar o sono", "Diminuir estresse e ansiedade", "Aumentar disposição e energia", "Reduzir inchaço", "Sentir minha casa mais leve"]))

# Última página: resultado e gravação de dados
def page_final():
    trigger_tracking_event("form_complete")

    st.success("Formulário concluído! Aqui está uma recomendação personalizada:")

    respostas = st.session_state.answers

    # Gerar texto personalizado
    recomendacoes = []
    if "dores" in respostas:
        if "Ombros/pescoço" in respostas["dores"]:
            recomendacoes.append("Considere uma massagem relaxante focada em pescoço e ombros.")
        if "Lombar" in respostas["dores"]:
            recomendacoes.append("Uma sessão terapêutica para a região lombar pode aliviar tensões.")
        if "Pernas/pés" in respostas["dores"]:
            recomendacoes.append("Massagens drenantes podem ajudar com retenção de líquidos.")

    if respostas.get("sono") == "Tenho dificuldade para dormir":
        recomendacoes.append("Terapias relaxantes podem auxiliar na melhora do sono.")

    if respostas.get("energia") == "Me sinto sem energia":
        recomendacoes.append("Experimente sessões revigorantes para aumentar sua energia.")

    st.write("\n".join(recomendacoes))

    # Salvar dados como exemplo
    st.subheader("Dados salvos:")
    dados_pessoais = {
        "nome": respostas.get("nome"),
        "cpf": respostas.get("cpf"),
        "data_nascimento": respostas.get("data_nascimento"),
        "genero": respostas.get("genero"),
        "celular": respostas.get("celular")
    }
    dados_avaliacao = {k: v for k, v in respostas.items() if k not in dados_pessoais}

    st.json({
        "dados_pessoais": dados_pessoais,
        "avaliacao": json.dumps(dados_avaliacao, ensure_ascii=False)
    })

pages.append(page_final)

# Executar a página atual
pages[st.session_state.page]()
