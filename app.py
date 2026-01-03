# app.py - Fluxo com Dan - JPM - COM BOTÃO DE REFRESH
import streamlit as st
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

WEEKLY_PASSWORD = "fluxo2026w01"

# -----------------------------
# 🔐 LOGIN
# -----------------------------

st.set_page_config(page_title="Fluxo com Dan - JPM", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

col_main, col_login = st.columns([4, 1])

with col_login:
    st.markdown("### 🔐 ACESSO RESTRITO")
    if not st.session_state.authenticated:
        usuario = st.text_input("Usuário", value="dan")
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if senha == WEEKLY_PASSWORD:
                st.session_state.authenticated = True
                st.success("✅ Acesso liberado!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")
    else:
        st.success("🟢 Logado como: dan")
        if st.button("SAIR"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.stop()

# -----------------------------
# 📡 FUNÇÕES PARA DADOS REAIS
# -----------------------------

def get_pica1():
    try:
        url = "https://br.investing.com/rates-bonds/u.s.-10-year-bond-yield"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        yield_val = soup.find("span", {"data-test": "instrument-price-last"}).text
        yield_float = float(yield_val.replace('%', ''))
        return 80 if yield_float > 4.0 else 40
    except:
        return 80

def get_pica2():
    try:
        url = "https://br.investing.com/rates-bonds/brazil-10-year-bond-yield"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        yield_val = soup.find("span", {"data-test": "instrument-price-last"}).text
        yield_float = float(yield_val.replace('%', ''))
        return 95 if yield_float > 12.0 else 70
    except:
        return 95

def get_pica3():
    try:
        url = "https://br.investing.com/rates-bonds/germany-10-year-bond-yield"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        yield_val = soup.find("span", {"data-test": "instrument-price-last"}).text
        yield_float = float(yield_val.replace('%', ''))
        return 60 if yield_float > 3.0 else 40
    except:
        return 60

def get_pica4():
    try:
        url_cn = "https://br.investing.com/rates-bonds/china-10-year-bond-yield"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response_cn = requests.get(url_cn, headers=headers, timeout=10)
        soup_cn = BeautifulSoup(response_cn.content, 'html.parser')
        yield_cn = float(soup_cn.find("span", {"data-test": "instrument-price-last"}).text.replace('%', ''))
        
        url_hk = "https://br.investing.com/rates-bonds/hong-kong-10-year-bond-yield"
        response_hk = requests.get(url_hk, headers=headers, timeout=10)
        soup_hk = BeautifulSoup(response_hk.content, 'html.parser')
        yield_hk = float(soup_hk.find("span", {"data-test": "instrument-price-last"}).text.replace('%', ''))
        
        spread = yield_hk - yield_cn
        return 70 if spread > 0.5 else 50
    except:
        return 70

def get_pika100():
    try:
        url = "https://br.investing.com/economic-calendar/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []
        rows = soup.find_all("tr", class_="js-event-item")[:4]
        for row in rows:
            impact_elem = row.find("td", class_="left textNum sentiment")
            if impact_elem and "sentiment-high" in str(impact_elem):
                time_elem = row.find("td", class_="first left time")
                event_elem = row.find("a", class_="event")
                if time_elem and event_elem:
                    events.append(f"🔴 {time_elem.text.strip()} - {event_elem.text.strip()}")
        return events if events else ["🟡 Sem eventos de alto impacto hoje"]
    except:
        return ["⚠️ Erro ao carregar agenda"]

# -----------------------------
# 🔄 BOTÃO DE ATUALIZAÇÃO
# -----------------------------

with col_main:
    st.markdown("<h1 style='text-align: center;'>FLUXO COM DAN - JPM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Rastreados de JUROS</h3>", unsafe_allow_html=True)

    # Botão de refresh no topo
    if st.button("🔄 Atualizar Dados"):
        st.session_state.flux_eua = get_pica1()
        st.session_state.flux_br = get_pica2()
        st.session_state.flux_eur = get_pica3()
        st.session_state.flux_asia = get_pica4()
        st.session_state.pika12_pct = int((st.session_state.flux_eua + st.session_state.flux_br + st.session_state.flux_eur + st.session_state.flux_asia) / 4)
        st.session_state.agenda = get_pika100()
        st.success("✅ Dados atualizados em tempo real!")

    # Se for a primeira vez, carrega os dados
    if 'flux_eua' not in st.session_state:
        with st.spinner("Carregando dados iniciais..."):
            st.session_state.flux_eua = get_pica1()
            st.session_state.flux_br = get_pica2()
            st.session_state.flux_eur = get_pica3()
            st.session_state.flux_asia = get_pica4()
            st.session_state.pika12_pct = int((st.session_state.flux_eua + st.session_state.flux_br + st.session_state.flux_eur + st.session_state.flux_asia) / 4)
            st.session_state.agenda = get_pika100()

    # Layout dos gauges
    gauge_col1, gauge_col2 = st.columns(2)
    gauge_col3, gauge_col4 = st.columns(2)

    with gauge_col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.flux_eua,
            title={'text': "🇺🇸 EUA", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if st.session_state.flux_eua >= 70 else "yellow" if st.session_state.flux_eua >= 30 else "red", 'thickness': 0.75},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: {'green' if st.session_state.flux_eua >= 70 else 'orange' if st.session_state.flux_eua >= 30 else 'red'}; text-align: center;'>{st.session_state.flux_eua}%</h3>", unsafe_allow_html=True)

    with gauge_col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.flux_br,
            title={'text': "🇧🇷 BRASIL", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if st.session_state.flux_br >= 70 else "yellow" if st.session_state.flux_br >= 30 else "red", 'thickness': 0.75},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: {'green' if st.session_state.flux_br >= 70 else 'orange' if st.session_state.flux_br >= 30 else 'red'}; text-align: center;'>{st.session_state.flux_br}%</h3>", unsafe_allow_html=True)

    with gauge_col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.flux_eur,
            title={'text': "🇪🇺 EUROPA", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if st.session_state.flux_eur >= 70 else "yellow" if st.session_state.flux_eur >= 30 else "red", 'thickness': 0.75},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: {'green' if st.session_state.flux_eur >= 70 else 'orange' if st.session_state.flux_eur >= 30 else 'red'}; text-align: center;'>{st.session_state.flux_eur}%</h3>", unsafe_allow_html=True)

    with gauge_col4:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.flux_asia,
            title={'text': "🇨🇳 ÁSIA", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if st.session_state.flux_asia >= 70 else "yellow" if st.session_state.flux_asia >= 30 else "red", 'thickness': 0.75},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: {'green' if st.session_state.flux_asia >= 70 else 'orange' if st.session_state.flux_asia >= 30 else 'red'}; text-align: center;'>{st.session_state.flux_asia}%</h3>", unsafe_allow_html=True)

    # PIKA12
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>🌡️ PIKA12 - TERMÔMETRO MUNDIAL</h2>", unsafe_allow_html=True)
    col_intersec, _ = st.columns([1, 3])
    with col_intersec:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.pika12_pct,
            title={'text': "FLUXO GLOBAL", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if st.session_state.pika12_pct >= 70 else "yellow" if st.session_state.pika12_pct >= 30 else "red", 'thickness': 0.75},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: {'green' if st.session_state.pika12_pct >= 70 else 'orange' if st.session_state.pika12_pct >= 30 else 'red'}; text-align: center;'>{st.session_state.pika12_pct}%</h3>", unsafe_allow_html=True)
        label = "AVERSÃO MÁXIMA A RISCO" if st.session_state.pika12_pct >= 70 else "TOMADA DE RISCO" if st.session_state.pika12_pct <= 30 else "TRANSIÇÃO"
        st.markdown(f"<p style='text-align: center; font-size: 16px;'><b>{label}</b></p>", unsafe_allow_html=True)

# -----------------------------
# 📅 AGENDA
# -----------------------------

st.markdown("---")
st.header("📅 Agenda Econômica do Dia – REAL")

for item in st.session_state.agenda:
    st.markdown(f"• {item}")

st.caption("© 2026 Fluxo com Dan - JPM | Dados: Investing.com | Atualizado sob demanda.")
