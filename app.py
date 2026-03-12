import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", layout="wide")

# 2. 상단 브랜드 섹션 (추가됨)
st.markdown("<h1 style='text-align: center; color: #2E8B57;'>나도 할 수 있다! 자산관리</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>누구나 쉽게 따라 할 수 있는 최적의 자산관리 시스템</h3>", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        leading_idx = 100.5   # 경기선행지수
        export_growth = 4.6   # 한국 수출 증가율
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 4. 자산별 비중 계산 로직
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

if vix > 25: vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "위험 관리"; gold_w += 15; stock_w -= 10
elif vix < 15: vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "주식 확대"; gold_w -= 10; stock_w += 20
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "보통"

if rsi > 65: rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "현금 확보"; cash_w += 15; stock_w -= 5
elif rsi < 35: rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "저가 매수"; cash_w -= 10; stock_w += 25
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "적정"

if leading_idx >= 100: eco_sig, eco_col, eco_desc = "확장", "#2E8B57", "주도주 집중"; stock_w += 25; bond_w -= 15
else: eco_sig, eco_col, eco_desc = "수축", "#FF4B4B", "방어 전략"; stock_w -= 10; bond_w += 10

if export_growth > 0: exp_sig, exp_col, exp_desc = "호조", "#2E8B57", "성장 가속"; stock_w += 20; gold_w -= 10
else: exp_sig, exp_col, exp_desc = "부진", "#FF4B4B", "보수 운용"; stock_w -= 15; cash_w += 10

if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30

total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100)
cash_w = 100 - (stock_w + bond_w + gold_w)

if bond_w < 20:
    diff = 20 - bond_w
    bond_w = 20
    stock_w -= diff

# 5. 투자 기상도
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

# 7. 핵심 지표 분석
st.subheader("🔍 핵심 지표 통합 분석")
m1, m2, m3, m4 = st.columns(4)
def mini_card(col, title, val, sig, color, desc, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 12px; margin:0; font-weight: bold;">{title} 🔗</p>
                <p style="font-size: 20px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 14px; font-weight: bold; margin:0;">{sig} ({desc})</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(m1, "공포 지수 (VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
mini_card(m2, "과열도 (RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")
mini_card(m3, "경기 선행 (지수)", leading_idx, eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수")
mini_card(m4, "한국 수출 (증가율)", f"{export_growth}%", exp_sig, exp_col, exp_desc, "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 상세 ETF 포트폴리오
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
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

# 9. 하단 서명 (추가됨)
st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
