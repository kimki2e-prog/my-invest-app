import streamlit as st
from PIL import Image
import yfinance as yf

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
        누구나 쉽게 따라 할 수 있는 최적의 자산관리 시스템 | 
        <span style='color: #FF4B4B; font-weight: bold;'>절대 잃지 않는 투자전략!</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 및 공포&탐욕 지수 산출
def get_market_indices():
    try:
        # VIX 및 RSI 데이터
        vix_data = yf.Ticker("^VIX").history(period="1d")
        vix = vix_data['Close'].iloc[-1]
        
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 공포 & 탐욕 지수 자체 계산 모델 (0~100)
        # VIX(변동성)와 RSI(과열도)를 조합하여 심리 점수 산출
        fg_val = 100 - (vix * 2) + (rsi - 50)
        fg_val = round(max(0, min(100, fg_val)))
        
        leading_idx = 100.5   # 경기선행지수 (고정 예시값)
        export_growth = 4.6   # 한국 수출 증가율 (고정 예시값)
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth, fg_val
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix, rsi, leading_idx, export_growth, fg_val = get_market_indices()

# 4. 자산별 비중 계산 로직
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

# VIX 기반 비중 조절
if vix > 25: vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "위험 관리"; gold_w += 15; stock_w -= 10
elif vix < 15: vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "주식 확대"; gold_w -= 10; stock_w += 20
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "보통"

# RSI 기반 비중 조절
if rsi > 65: rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "현금 확보"; cash_w += 15; stock_w -= 5
elif rsi < 35: rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "저가 매수"; cash_w -= 10; stock_w += 25
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "적정"

# 경기 및 수출 지표 기반 조절
eco_sig, eco_col, eco_desc = ("확장", "#2E8B57", "주도주 집중") if leading_idx >= 100 else ("수축", "#FF4B4B", "방어 전략")
exp_sig, exp_col, exp_desc = ("호조", "#2E8B57", "성장 가속") if export_growth > 0 else ("부진", "#FF4B4B", "보수 운용")

# 공포 & 탐욕 지수 상태 판별
if fg_val >= 75: fg_sig, fg_col, fg_desc = "극도의 탐욕", "#FF4B4B", "과열 주의"
elif fg_val >= 55: fg_sig, fg_col, fg_desc = "탐욕", "#FFA500", "비중 조절"
elif fg_val <= 25: fg_sig, fg_col, fg_desc = "극도의 공포", "#2E8B57", "저가 매수"
elif fg_val <= 45: fg_sig, fg_col, fg_desc = "공포", "#3CB371", "관심 필요"
else: fg_sig, fg_col, fg_desc = "중립", "#6C757D", "보통"

# 비중 제약 조건 및 정규화
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100)
cash_w = 100 - (stock_w + bond_w + gold_w)
if bond_w < 20: stock_w -= (20 - bond_w); bond_w = 20

# 5. 투자 기상도
weather, w_icon, w_col = ("공격적 확장", "🚀", "#2E8B57") if stock_w >= 70 else (("안정적 수익", "☀️", "#3CB371") if stock_w >= 50 else ("보수적 대응", "☁️", "#FFA500"))
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

# 7. 핵심 지표 통합 분석 (5열 배치 및 상세 툴팁)
st.subheader("🔍 핵심 지표 통합 분석")
st.caption("💡 각 지표 카드에 마우스를 올리면 상세 설명을 확인할 수 있습니다.")

m1, m2, m3, m4, m5 = st.columns(5)

vix_tip = "VIX(공포지수)는 시장의 변동성 기대를 나타냅니다. 20-30 이상으로 높으면 시장이 불안하다는 신호입니다."
rsi_tip = "RSI는 주가의 과열 정도를 측정합니다. 70 이상은 과열, 30 이하는 과매도 상태로 봅니다."
fg_tip = "공포&탐욕 지수는 투자 심리를 0(공포)에서 100(탐욕)으로 수치화한 것입니다. 극도의 공포는 매수 기회일 수 있습니다."
leading_tip = "경기선행지수는 향후 경기를 예측합니다. 100 이상이면 경기 확장을 의미합니다."
export_tip = "한국의 수출 실적입니다. 증가율이 높을수록 국내 증시 기초체력이 튼튼함을 뜻합니다."

def mini_card(col, title, val, sig, color, desc, link, help_text):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;" title="{help_text}">
            <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p>
                <p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p>
                <p style="color: #999; font-size: 11px; margin:0;">({desc})</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(m1, "변동성 (VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index", vix_tip)
mini_card(m2, "과열도 (RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI", rsi_tip)
mini_card(m3, "공포&탐욕 지수", fg_val, fg_sig, fg_col, fg_desc, "https://edition.cnn.com/markets/fear-and-greed", fg_tip)
mini_card(m4, "경기선행지수", leading_idx, eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수", leading_tip)
mini_card(m5, "한국 수출실적", f"{export_growth}%", exp_sig, exp_col, exp_desc, "https://www.google.com/search?q=수출입동향", export_tip)

st.divider()

# 8. 상세 ETF 포트폴리오
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
col_st, col_bd, col_gd = st.columns(3)
with col_st:
    st.markdown("#### 📈 주식 (Growth)\n**🇰🇷 국내**: Tiger 200, 코리아밸류업\n**🇺🇸 미국**: S&P500, 나스닥100, AI테마")
with col_bd:
    st.markdown("#### 🏦 채권 (Safety)\n**🇺🇸 미국채**: 30년국채액티브(H), 10년국채\n**🇰🇷 국고채**: 국고채10년")
with col_gd:
    st.markdown("#### 🟡 금/현금 (Hedge)\n**금**: ACE KRX금현물\n**현금**: CD금리액티브")

st.divider()

# 9. 자산관리 구성의 논리
st.subheader("💡 좋은투자자의 자산배분 철학")
with st.expander("🧐 비중 설정의 근거가 궁금하신가요?", expanded=True):
    st.markdown("""
    * **주식**: 성장의 엔진으로서 최소 30%는 유지하여 시장 반등에 소외되지 않도록 합니다.
    * **채권**: 하락장의 에어백입니다. 어떤 상황에서도 최소 20%를 확보해 심리적 안정을 돕습니다.
    * **금/원자재**: 포트폴리오의 보험료 개념으로 최대 15% 이내에서 조절합니다.
    """)

# 10. 하단 서명
st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
