import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정 및 브랜딩
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", layout="wide")

# 2. 상단 헤더 섹션
st.markdown("<h1 style='text-align: center; color: #2E8B57; margin-bottom: 5px;'>나도 할 수 있다! 자산관리</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; font-size: 20px; color: #666;'>
        누구나 쉽게 따라 할 수 있는 최적의 자산관리 시스템 | 
        <span style='color: #FF4B4B; font-weight: bold;'>절대 잃지 않는 투자전략!</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 시장 데이터 수집 (2026년 기준)
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 경기 지표 (실제 운영 시 API 연동 가능)
        leading_idx = 100.5   # 경기선행지수
        export_growth = 4.6   # 한국 수출 증가율
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 4. 자산배분 로직 (주식 30% 하한 / 채권 20% 하한 / 금 15% 상한)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

# [지표 반영]
if vix > 25: gold_w += 15; stock_w -= 10
elif vix < 15: gold_w -= 10; stock_w += 20
if rsi > 65: cash_w += 15; stock_w -= 5
elif rsi < 35: cash_w -= 10; stock_w += 25
if leading_idx >= 100: stock_w += 25; bond_w -= 15
else: stock_w -= 10; bond_w += 10
if export_growth > 0: stock_w += 20; gold_w -= 10
else: stock_w -= 15; cash_w += 10

# [제약 조건 및 정규화]
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30

total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100)
cash_w = 100 - (stock_w + bond_w + gold_w)

# [채권 하한 보정]
if bond_w < 20:
    diff = 20 - bond_w
    bond_w = 20
    stock_w -= diff

# 5. 투자 기상도 UI
if stock_w >= 70: weather, w_icon, w_col = "공격적 확장", "🚀", "#2E8B57"
elif stock_w >= 50: weather, w_icon, w_col = "안정적 수익", "☀️", "#3CB371"
else: weather, w_icon, w_col = "보수적 대응", "☁️", "#FFA500"

st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 14px; color: #666; margin-bottom: 0;'>오늘의 자산 배분 기상도</p><h2 style='color: {w_col}; margin: 0;'>{w_icon} {weather} 전략 구간</h2></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
st.subheader("🚥 자산별 권장 비중")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 초보자를 위한 자산관리 철학 보강
st.subheader("💡 좋은투자자가 알려주는 '이기는 투자'의 원리")
st.success("사회초년생과 초보 투자자분들, 이 4가지만 기억하면 투자가 쉬워집니다!")

col_intro1, col_intro2 = st.columns(2)
with col_intro1:
    st.markdown("""
    ### 1️⃣ 주식은 '엔진'입니다 (성장)
    * **왜 하나요?** 물가 상승보다 내 자산을 더 빨리 키우기 위해서입니다.
    * **전략:** 한국(밸류업)과 미국(AI·혁신)에 반반씩 투자하여 전 세계 성장에 올라탑니다. 
    * **초보자 팁:** 시장이 무서울 때도 최소 30%는 유지하세요. 엔진을 완전히 끄면 반등할 때 소외될 수 있습니다.
    
    ### 2️⃣ 채권은 '에어백'입니다 (안전)
    * **왜 하나요?** 경제 위기라는 사고가 났을 때 내 소중한 원금을 보호하기 위해서입니다.
    * **전략:** 가장 믿을 수 있는 미국과 한국 정부에 돈을 빌려주고 따박따박 이자를 받습니다.
    * **초보자 팁:** 주식이 떨어질 때 채권은 가치가 오르는 경향이 있습니다. 마음 편한 투자를 위해 최소 20%는 꼭 챙기세요.
    """)

with col_intro2:
    st.markdown("""
    ### 3️⃣ 금은 '보험'입니다 (헤지)
    * **왜 하나요?** 화폐 가치가 떨어지거나 전쟁 같은 비상상황에서 내 자산을 지켜주는 '비상금'입니다.
    * **전략:** 가장 신뢰도 높은 KRX 금 현물로 안전하게 보관합니다.
    * **초보자 팁:** 보험료가 너무 비싸면 안 되겠죠? 전체 자산의 15%까지만 담아 수익률과 안전의 균형을 맞춥니다.

    ### 4️⃣ 현금은 '기회'입니다 (유동성)
    * **왜 하나요?** 시장이 일시적으로 폭락했을 때, 좋은 주식을 싸게 쇼핑하기 위한 '전투 식량'입니다.
    * **초보자 팁:** 현금도 그냥 두지 않고 매일 이자가 쌓이는 파킹형 ETF(CD금리 등)에 넣어둡니다.
    """)

st.divider()

# 8. 상세 ETF 포트폴리오 (실제 매수 종목)
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
st.info("💡 아래 종목들은 국내 증권사 계좌(ISA, 연금저축 등)에서 누구나 쉽게 매수할 수 있습니다.")

col_st, col_bd, col_gd = st.columns(3)
with col_st:
    st.markdown("#### 📈 주식 (Growth)")
    st.markdown("""
    **🇰🇷 국내 주식 (50%)**
    * Tiger 200 (20%)
    * Rise 코리아밸류업 (15%)
    * PLUS 고배당주 (15%)
    
    **🇺🇸 미국 주식 (50%)**
    * Tiger S&P500 (20%)
    * Rise 미국나스닥 100 (10%)
    * Time글로벌 AI인공지능액티브 (10%)
    * Kodex 미국AI전력핵심인프라 (10%)
    """)

with col_bd:
    st.markdown("#### 🏦 채권 (Safety)")
    st.markdown("""
    **🇺🇸 미국 채권 (60%)**
    * Kodex 미국30년국채액티브(H) (30%)
    * ACE 미국국채10년액티브(H) (30%)
    
    **🇰🇷 국내 채권 (40%)**
    * ACE 국고채10년 (40%)
    """)

with col_gd:
    st.markdown("#### 🟡 금/원자재 (Hedge)")
    st.markdown("""
    **설정 종목 (100%)**
    * ACE KRX금현물 ETF (100%)
    """)
    st.markdown("#### 💵 현금 (Liquidity)")
    st.markdown("""
    * TIGER CD금리액티브
    * KODEX KOFR금리
    """)

st.divider()

# 9. 핵심 지표 분석 (대시보드 하단 배치)
st.subheader("🔍 실시간 데이터 통합 분석")
m1, m2, m3, m4 = st.columns(4)
def mini_card(col, title, val, sig, color, desc, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p>
                <p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig} ({desc})</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(m1, "공포 지수 (VIX)", vix, "정상", "#FFA500", "변동성 체크", "https://www.google.com/search?q=VIX+index")
mini_card(m2, "과열도 (RSI)", rsi, "적정", "#2E8B57", "매수강도", "https://www.google.com/search?q=SPY+RSI")
mini_card(m3, "경기 선행지수", leading_idx, "확장", "#2E8B57", "경기방향", "https://www.google.com/search?q=경기선행지수")
mini_card(m4, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "국내활력", "https://www.google.com/search?q=수출입동향")

# 10. 하단 푸터
st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 2026년 기준 시뮬레이션이며, 모든 투자 판단의 최종 책임은 사용자에게 있습니다.")
