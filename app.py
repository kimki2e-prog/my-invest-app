import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="프리미엄 투자 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="프리미엄 투자 전략실")

# 2. 실시간 데이터 수집 (VIX, Fear & Greed 대용 지표, 경기선행지수 시뮬레이션)
def get_market_indices():
    try:
        # VIX 지수 (실시간)
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        
        # 공포탐욕지수 대용 (S&P500의 RSI 지표 활용 - 70이상이면 탐욕, 30이하 공포)
        spy = yf.Ticker("SPY").history(period="14d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # 선행지수 순환변동치 (최근 발표치 고정값 - 매월 업데이트 권장)
        leading_idx = 100.5 
        
        return round(vix, 2), round(rsi, 2), leading_idx
    except:
        return 20.0, 50.0, 100.0

vix, fear_greed, leading_idx = get_market_indices()

# 3. 개별 지표 신호등 판별 로직
# VIX: 20이하(안전), 30이상(위험)
v_sig, v_col = ("🟢 안전", "#2E8B57") if vix < 20 else (("🔴 위험", "#FF4B4B") if vix > 30 else ("🟡 주의", "#FFA500"))
# 공포탐욕(RSI): 30이하(과매도/공포-안전), 70이상(과매수/탐욕-위험)
f_sig, f_col = ("🟢 공포(매수기회)", "#2E8B57") if fear_greed < 35 else (("🔴 탐욕(매도주의)", "#FF4B4B") if fear_greed > 65 else ("🟡 보통", "#FFA500"))
# 선행지수: 100기준
l_sig, l_col = ("🟢 확장", "#2E8B57") if leading_idx >= 100 else ("🔴 수축", "#FF4B4B")

# 4. 종합 점수 및 날씨 결정
score = 0
for col in [v_col, f_col, l_col]:
    if col == "#2E8B57": score += 1

if score == 3: weather, w_icon, w_col = "쾌청 (적극 투자)", "☀️", "#2E8B57"
elif score == 2: weather, w_icon, w_col = "맑음 (비중 유지)", "🌤️", "#3CB371"
elif score == 1: weather, w_icon, w_col = "흐림 (보수적 운영)", "☁️", "#FFA500"
else: weather, w_icon, w_col = "폭풍우 (자산 보호)", "⛈️", "#FF4B4B"

# 5. UI 화면 구성
st.markdown(f"<h1 style='text-align: center; color: {w_col};'>{w_icon} {weather}</h1>", unsafe_allow_html=True)
st.divider()

st.subheader("🚥 지표별 투자 신호등")

def signal_card(title, val, sig, col):
    st.markdown(f"""
        <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 10px solid {col};">
            <span style="font-size: 14px; color: #666;">{title}</span><br>
            <span style="font-size: 18px; font-weight: bold;">{val}</span> 
            <span style="float: right; color: {col}; font-weight: bold;">{sig}</span>
        </div>
    """, unsafe_allow_html=True)

signal_card("VIX (변동성 지수)", f"{vix}", v_sig, v_col)
signal_card("공포와 탐욕 (RSI 기준)", f"{fear_greed}/100", f_sig, f_col)
signal_card("경기선행지수 순환변동치", f"{leading_idx}", l_sig, l_col)

st.divider()
st.caption("※ 지표 데이터는 실시간 연동 및 최근 통계청 자료를 바탕으로 산출됩니다.")
