import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="투자 기상청", page_icon=img)
except:
    st.set_page_config(page_title="투자 기상청")

# 2. 실시간 데이터 가져오기 (에러 방지 로직 추가)
def get_market_data():
    try:
        # VIX 데이터를 가져옵니다
        vix_ticker = yf.Ticker("^VIX")
        # 안전하게 최근 5일치 데이터를 가져와서 마지막 값을 씁니다
        vix_history = vix_ticker.history(period="5d")
        
        if not vix_history.empty:
            current_vix = vix_history['Close'].iloc[-1]
            return round(current_vix, 2)
        else:
            return 20.0  # 데이터를 못 가져오면 '보통' 수준인 20으로 설정
    except:
        return 20.0  # 에러 발생 시 기본값 20 반환

# 3. 데이터 로드
vix = get_market_data()

# 4. 날씨 및 비중 결정
if vix > 30:
    weather, color, advice = "⛈️ 폭풍우", "#FF4B4B", "매우 위험! 현금을 확보하세요."
    stock, bond, cash = 20, 50, 30
elif vix > 20:
    weather, color, advice = "☁️ 흐림", "#FFA500", "주의가 필요합니다. 무리하지 마세요."
    stock, bond, cash = 40, 40, 20
else:
    weather, color, advice = "☀️ 맑음", "#2E8B57", "시장이 안정적입니다. 계획대로 투자하세요."
    stock, bond, cash = 60, 30, 10

# 5. UI 그리기
col1, col2, col3 = st.columns([1,1,1])
with col2:
    try: st.image("logo.png", width=120)
    except: pass

st.markdown(f"<h1 style='text-align: center; color: {color};'>{weather}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>현재 시장 공포지수(VIX): <b>{vix}</b></p>", unsafe_allow_html=True)

st.info(f"💡 **오늘의 가이드:** {advice}")

st.divider()

st.subheader("🚥 추천 자산 비중")
c1, c2, c3 = st.columns(3)
c1.metric("주식", f"{stock}%")
c2.metric("채권", f"{bond}%")
c3.metric("현금", f"{cash}%")
