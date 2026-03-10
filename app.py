import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="중기 자산배분 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="중기 자산배분 전략실")

# 2. 데이터 수집 함수
def get_market_indices():
    try:
        # VIX (실시간 심리)
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        
        # 공포탐욕 대용 (RSI)
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 경기선행지수 순환변동치 (한국 통계청 최근 발표치 반영)
        leading_idx = 100.5 
        
        return round(vix, 2), round(rsi, 2), leading_idx
    except:
        return 20.0, 50.0, 100.0

vix, rsi, leading_idx = get_market_indices()

# 3. 개별 신호등 판별
v_sig, v_col = ("안전", "#2E8B57") if vix < 20 else (("위험", "#FF4B4B") if vix > 30 else ("주의", "#FFA500"))
f_sig, f_col = ("기회", "#2E8B57") if rsi < 35 else (("과열", "#FF4B4B") if rsi > 65 else ("보통", "#FFA500"))
l_sig, l_col = ("확장", "#2E8B57") if leading_idx >= 100 else ("수축", "#FF4B4B")

# 4. [신규] 3~6개월 중기 주식 비중 계산 로직
# 기본 비중 50%에서 시작하여 지표별로 가감합니다.
stock_weight = 50
if leading_idx >= 100: stock_weight += 20  # 경기 확장기면 +20%
else: stock_weight -= 20                 # 경기 수축기면 -20%

if rsi > 65: stock_weight -= 10          # 시장 과열시 -10%
elif rsi < 35: stock_weight += 10       # 시장 공포시 +10%

if vix > 30: stock_weight -= 10          # 단기 불안시 -10%

# 비중 범위 제한 (최소 20% ~ 최대 90%)
stock_weight = max(20, min(90, stock_weight))

# 5. 종합 날씨 결정
if stock_weight >= 70: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 50: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 35: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "비", "⛈️", "#FF4B4B"

# 6. UI 구성
st.markdown(f"<h1 style='text-align: center; color: {w_col};'>{w_icon} {weather}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>향후 3~6개월 권장 주식 비중: {stock_weight}%</h3>", unsafe_allow_html=True)

st.divider()

# 지표별 신호등 표시
st.subheader("🚥 현재 시장 신호등")
col1, col2, col3 = st.columns(3)

def mini_card(col, title, val, sig, color):
    col.markdown(f"""
        <div style="background-color: #f8f9fb; padding: 10px; border-radius: 10px; border-top: 5px solid {color}; text-align: center;">
            <small>{title}</small><br>
            <span style="font-size: 18px; font-weight: bold;">{val}</span><br>
            <span style="color: {color}; font-weight: bold;">{sig}</span>
        </div>
    """, unsafe_allow_html=True)

mini_card(col1, "변동성(VIX)", vix, v_sig, v_col)
mini_card(col2, "심리(RSI)", rsi, f_sig, f_col)
mini_card(col3, "경기(선행)", leading_idx, l_sig, l_col)

st.divider()

# 자산배분 가이드 대시보드
st.subheader("📅 3~6개월 자산배분 가이드")
st.progress(stock_weight / 100) # 비중 시각화 바

c1, c2 = st.columns(2)
with c1:
    st.write(f"**주식 비중: {stock_weight}%**")
    st.write(f"**안전자산: {100 - stock_weight}%**")
with c2:
    if stock_weight >= 70:
        st.success("경기 확장 국면입니다. 우량주 중심의 공격적 투자가 유효합니다.")
    elif stock_weight >= 40:
        st.warning("중립적인 구간입니다. 배당주나 현금 비중을 적절히 유지하세요.")
    else:
        st.error("경기 수축 및 심리 불안 구간입니다. 보수적인 자산 방어가 최우선입니다.")

st.caption("※ 본 가이드는 VIX, RSI, 선행지수를 종합한 모델이며 투자 최종 결정은 본인에게 있습니다.")
