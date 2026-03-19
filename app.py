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
st.markdown("""
    <p style='text-align: center; font-size: 20px; color: #666;'>
        초보자를 위한 <span style='color: #2E8B57; font-weight: bold;'>분기별 정기 리밸런싱</span> 시스템 | 
        <span style='color: #FF4B4B; font-weight: bold;'>절대 잃지 않는 투자전략!</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 (분기 평균 및 실시간 데이터 분리)
@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신
def get_market_indices():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # [분기 평균용] VIX 및 RSI
        vix_df = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        vix_avg = vix_df['Close'].mean()
        
        spy_df = yf.download("SPY", start=start_date, end=end_date, progress=False)
        delta = spy_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_series = 100 - (100 / (1 + (gain / loss)))
        rsi_avg = rsi_series.mean()

        # [실시간 반영용] 공포 & 탐욕 지수
        vix_now = vix_df['Close'].iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        fg_now = 100 - (vix_now * 2) + (rsi_now - 50)
        fg_now = round(max(0, min(100, fg_now)))
        
        leading_idx = 100.5   
        export_growth = 4.6   
        
        return round(vix_avg, 2), round(rsi_avg, 2), leading_idx, export_growth, fg_now
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix_avg, rsi_avg, leading_idx, export_growth, fg_val = get_market_indices()

# 4. 자산별 비중 계산 로직
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

# VIX/RSI 지표 기반 조정
vix_sig, vix_col, vix_desc = ("주의", "#FF4B4B", "방어 강화") if vix_avg > 22 else (("안정", "#2E8B57", "비중 유지") if vix_avg < 16 else ("적정", "#FFA500", "보통"))
if vix_avg > 22: gold_w += 10; stock_w -= 5
elif vix_avg < 16: stock_w += 10

rsi_sig, rsi_col, rsi_desc = ("과열", "#FF4B4B", "점진 매도") if rsi_avg > 60 else (("저평가", "#2E8B57", "분할 매수") if rsi_avg < 40 else ("중립", "#FFA500", "적정"))
if rsi_avg > 60: cash_w += 10; stock_w -= 5
elif rsi_avg < 40: stock_w += 15

# 실시간 공포 & 탐욕 심리 판별
if fg_val >= 75: fg_sig, fg_col, fg_desc = "극도의 탐욕", "#FF4B4B", "과열 주의"
elif fg_val <= 25: fg_sig, fg_col, fg_desc = "극도의 공포", "#2E8B57", "매수 기회"
elif fg_val >= 55: fg_sig, fg_col, fg_desc = "탐욕", "#FFA500", "추격 금지"
elif fg_val <= 45: fg_sig, fg_col, fg_desc = "공포", "#3CB371", "분할 매수"
else: fg_sig, fg_col, fg_desc = "중립", "#6C757D", "관찰"

# 비중 정규화 (Min/Max 가이드라인 적용)
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100); bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100); cash_w = 100 - (stock_w + bond_w + gold_w)
if bond_w < 20: stock_w -= (20 - bond_w); bond_w = 20

# ---------------------------------------------------------
# 5. [투자 금액 산출기] 사이드바 설정
# ---------------------------------------------------------
st.sidebar.header("💰 나의 투자 금액 계산기")
input_money = st.sidebar.number_input("총 투자 원금을 입력하세요 (단위: 만원)", min_value=0, value=1000, step=10)
st.sidebar.divider()

# 자산군별 할당 금액 계산
m_stock = input_money * (stock_w / 100)
m_bond = input_money * (bond_w / 100)
m_gold = input_money * (gold_w / 100)
m_cash = input_money * (cash_w / 100)

st.sidebar.subheader("📍 자산별 매수 요약")
st.sidebar.markdown(f"📈 주식: **{round(m_stock)}** 만원")
st.sidebar.markdown(f"🏦 채권: **{round(m_bond)}** 만원")
st.sidebar.markdown(f"🟡 금: **{round(m_gold)}** 만원")
st.sidebar.markdown(f"💵 현금: **{round(m_cash)}** 만원")
st.sidebar.info("아래 '종목별 상세 매수 가이드'의 금액을 확인하세요!")

# 6. 분기별 안내 및 비중 카드
now = datetime.now()
quarter = (now.month - 1) // 3 + 1
st.info(f"📅 **현재는 {now.year}년 {quarter}분기 전략 구간입니다.**")

st.subheader("🚥 이번 분기 권장 비중 및 매수 금액")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color, amount):
    col.markdown(f"""
        <div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'>
            <h4 style='color: {color}; margin: 0;'>{title}</h4>
            <h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1>
            <p style='color: #333; font-weight: bold; margin: 0;'>총 {round(amount)}만원</p>
        </div>
    """, unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57", m_stock)
asset_card(c2, "채권", bond_w, "#007BFF", m_bond)
asset_card(c3, "금/원자재", gold_w, "#FFD700", m_gold)
asset_card(c4, "현금", cash_w, "#6C757D", m_cash)

st.divider()

# 7. 핵심 지표 분석 (생략 없이 유지)
st.subheader("🔍 핵심 지표 통합 분석")
m1, m2, m3, m4, m5 = st.columns(5)
def mini_card(col, title, val, sig, color, desc, link):
    col.markdown(f"""<a href="{link}" target="_blank" style="text-decoration: none;"><div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;"><p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p><p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p><p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p><p style="color: #999; font-size: 11px; margin:0;">({desc})</p></div></a>""", unsafe_allow_html=True)

mini_card(m1, "3개월 변동성(VIX)", vix_avg, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
mini_card(m2, "3개월 과열도(RSI)", rsi_avg, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")
mini_card(m3, "공포&탐욕(실시간)", fg_val, fg_sig, fg_col, fg_desc, "https://edition.cnn.com/markets/fear-and-greed")
mini_card(m4, "경기선행지수", leading_idx, "확장", "#2E8B57", "주도주 집중")
mini_card(m5, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "성장 가속")

st.divider()

# 8. [핵심 기능] 종목별 상세 매수 가이드 (금액 포함)
st.subheader("📦 종목별 상세 매수 가이드")
st.success(f"💡 **{input_money}만원** 기준, 각 ETF 종목별로 매수해야 할 구체적인 금액입니다.")
col_st, col_bd, col_gd = st.columns(3)

with col_st:
    st.markdown("#### 📈 주식 (Growth)")
    st.markdown(f"""
    **🇰🇷 국내 주식 (약 {round(m_stock*0.5)}만원)**
    * Tiger 200 (20%): **{round(m_stock*0.20)}** 만원
    * Rise 코리아밸류업 (15%): **{round(m_stock*0.15)}** 만원
    * PLUS 고배당주 (15%): **{round(m_stock*0.15)}** 만원
    
    **🇺🇸 미국 주식 (약 {round(m_stock*0.5)}만원)**
    * Tiger S&P500 (20%): **{round(m_stock*0.20)}** 만원
    * Rise 미국나스닥 100 (10%): **{round(m_stock*0.10)}** 만원
    * 글로벌 AI테마 (각 10%): **{round(m_stock*0.20)}** 만원
    """)

with col_bd:
    st.markdown("#### 🏦 채권 (Safety)")
    st.markdown(f"""
    **🇺🇸 미국 채권 (60%)**
    * Kodex 미국30년/10년 국채: **{round(m_bond*0.60)}** 만원
    
    **🇰🇷 국내 채권 (40%)**
    * ACE 국고채10년: **{round(m_bond*0.40)}** 만원
    """)

with col_gd:
    st.markdown("#### 🟡 금 & 현금 (Hedge)")
    st.markdown(f"""
    **금/원자재 (100%)**
    * ACE KRX금현물: **{round(m_gold)}** 만원
    
    **현금성 자산 (100%)**
    * 파킹형 ETF(CD금리 등): **{round(m_cash)}** 만원
    """)

st.divider()

# 9. 자산관리 철학 (무삭제 상세 버전 유지)
st.subheader("💡 좋은투자자의 자산배분 철학")
with st.expander("🧐 왜 주식/채권/금 비중을 이렇게 구성했나요?", expanded=True):
    st.markdown("""
    본 시스템은 **'지키면서 불리는'** 자산배분의 정석을 따릅니다. 
    3개월 평균 데이터를 통해 시장의 소음(Noise)을 제거하고 큰 흐름에 몸을 싣는 가장 현명한 리밸런싱을 제안합니다.
    """)

st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
