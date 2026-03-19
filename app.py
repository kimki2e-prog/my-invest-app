import streamlit as st
from PIL import Image
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", layout="wide")

# 2. 상단 브랜드 섹션
st.markdown("<h1 style='text-align: center; color: #2E8B57; margin-bottom: 5px;'>나도 할 수 있다! 자산관리</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px; color: #666;'>초보자를 위한 <span style='color: #2E8B57; font-weight: bold;'>분기별 정기 리밸런싱</span> 시스템</p>", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 로직 (캐싱 적용으로 속도 개선)
@st.cache_data(ttl=3600)
def get_market_indices():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        vix_df = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        vix_avg = vix_df['Close'].mean()
        spy_df = yf.download("SPY", start=start_date, end=end_date, progress=False)
        delta = spy_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_series = 100 - (100 / (1 + (gain / loss)))
        rsi_avg = rsi_series.mean()
        vix_now = vix_df['Close'].iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        fg_now = 100 - (vix_now * 2) + (rsi_now - 50)
        fg_now = round(max(0, min(100, fg_now)))
        return round(vix_avg, 2), round(rsi_avg, 2), 100.5, 4.6, fg_now
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix_avg, rsi_avg, leading_idx, export_growth, fg_val = get_market_indices()

# 4. 자산 비중 계산 (그레이엄 가이드라인 기반)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15
if vix_avg > 22: gold_w += 10; stock_w -= 5
elif vix_avg < 16: stock_w += 10
if rsi_avg > 60: cash_w += 10; stock_w -= 5
elif rsi_avg < 40: stock_w += 15

# 비중 정규화
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100); bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100); cash_w = 100 - (stock_w + bond_w + gold_w)
if bond_w < 20: stock_w -= (20 - bond_w); bond_w = 20

# 5. [금액 계산기] 사이드바 설정
st.sidebar.header("💰 나의 투자 금액 계산기")
input_money = st.sidebar.number_input("총 투자 원금을 입력하세요 (단위: 만원)", min_value=0, value=1000, step=10)
st.sidebar.divider()

# 자산군별 할당 총액
m_stock = input_money * (stock_w / 100)
m_bond = input_money * (bond_w / 100)
m_gold = input_money * (gold_w / 100)
m_cash = input_money * (cash_w / 100)

st.sidebar.subheader("📍 요약 안내")
st.sidebar.write(f"현재 원금 **{input_money}만원** 기준")
st.sidebar.info(f"주식 매수 총액: **{round(m_stock)}만원**")

# 6. 메인 화면: 비중 카드
st.subheader("🚥 이번 분기 권장 비중 및 매수 금액")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color, amount):
    col.markdown(f"""
        <div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'>
            <h4 style='color: {color}; margin: 0;'>{title}</h4>
            <h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1>
            <p style='color: #333; font-weight: bold;'>총 {round(amount)}만원</p>
        </div>
    """, unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57", m_stock)
asset_card(c2, "채권", bond_w, "#007BFF", m_bond)
asset_card(c3, "금/원자재", gold_w, "#FFD700", m_gold)
asset_card(c4, "현금", cash_w, "#6C757D", m_cash)

st.divider()

# 9. 상세 ETF 포트폴리오 (종목별 매수 금액 상세 산출)
st.subheader("📦 종목별 상세 매수 가이드")
st.success(f"💡 **{input_money}만원** 투자 시, 아래 적힌 금액만큼 각 종목을 매수하시면 됩니다.")

col_st, col_bd, col_gd = st.columns(3)

with col_st:
    st.markdown("#### 📈 주식 (Growth)")
    # 주식군 내 세부 금액 계산
    m_kor_stock = m_stock * 0.5  # 국내 주식 50%
    m_us_stock = m_stock * 0.5   # 미국 주식 50%
    
    st.markdown(f"**🇰🇷 국내 주식 세부 (약 {round(m_kor_stock)}만원)**")
    st.markdown(f"* Tiger 200 (20%): **{round(m_stock * 0.20)}** 만원")
    st.markdown(f"* Rise 코리아밸류업 (15%): **{round(m_stock * 0.15)}** 만원")
    st.markdown(f"* PLUS 고배당주 (15%): **{round(m_stock * 0.15)}** 만원")
    
    st.write("") # 간격 조절
    st.markdown(f"**🇺🇸 미국 주식 세부 (약 {round(m_us_stock)}만원)**")
    st.markdown(f"* Tiger S&P500 (20%): **{round(m_stock * 0.20)}** 만원")
    st.markdown(f"* Rise 미국나스닥 100 (10%): **{round(m_stock * 0.10)}** 만원")
    st.markdown(f"* 글로벌 AI 및 테마 (20%): **{round(m_stock * 0.20)}** 만원")

with col_bd:
    st.markdown("#### 🏦 채권 (Safety)")
    st.markdown(f"**🇺🇸 미국 채권 (60%)**")
    st.markdown(f"* 미국 30년/10년 국채: **{round(m_bond * 0.60)}** 만원")
    
    st.write("") 
    st.markdown(f"**🇰🇷 국내 채권 (40%)**")
    st.markdown(f"* ACE 국고채10년: **{round(m_bond * 0.40)}** 만원")

with col_gd:
    st.markdown("#### 🟡 금 & 현금 (Hedge)")
    st.markdown(f"**금/원자재 (100%)**")
    st.markdown(f"* ACE KRX금현물: **{round(m_gold)}** 만원")
    
    st.write("") 
    st.markdown(f"**현금성 자산 (100%)**")
    st.markdown(f"* 파킹형 ETF (CD금리 등): **{round(m_cash)}** 만원")

st.divider()

# 자산관리 철학 (요약)
with st.expander("🧐 자산배분 계산 논리 확인하기"):
    st.write(f"""
    1. 총 원금 **{input_money}만원**에서 현재 시장 지표에 따른 자산군 비중을 곱합니다.
    2. 산출된 자산군별 금액에서 각 전략별(국내/해외 등) 세부 비율을 다시 곱하여 종목별 최종 금액을 도출합니다.
    3. 모든 금액은 초보 투자자의 편의를 위해 만 원 단위에서 반올림 처리되었습니다.
    """)

st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
