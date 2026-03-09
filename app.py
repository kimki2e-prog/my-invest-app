import streamlit as st
from PIL import Image
import yfinance as yf # 실시간 금융 데이터를 가져오는 도구

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="투자 기상청", page_icon=img)
except:
    st.set_page_config(page_title="투자 기상청")

# 2. 실시간 데이터 가져오기 함수
def get_market_data():
    # VIX 지수(공포지수) 가져오기
    vix_data = yf.Ticker("^VIX").history(period="1d")
    current_vix = vix_data['Close'].iloc[-1]
    return round(current_vix, 2)

# 3. 로직: VIX 지수에 따른 날씨 결정
vix = get_market_data()

if vix > 30:
    weather = "⛈️ 폭풍우 (매우 위험)"
    advice = "시장이 매우 불안합니다. 현금을 최대한 확보하세요!"
    stock_p, bond_p, cash_p = 20, 50, 30
elif vix > 20:
    weather = "☁️ 흐림 (주의)"
    advice = "변동성이 커지고 있습니다. 무리한 추격 매수는 금물!"
    stock_p, bond_p, cash_p = 40, 40, 20
else:
    weather = "☀️ 맑음 (안정)"
    advice = "시장이 평온합니다. 계획대로 투자를 진행하세요."
    stock_p, bond_p, cash_p = 60, 30, 10

# 4. 화면 UI 그리기
col1, col2, col3 = st.columns([1,1,1])
with col2:
    st.image("logo.png", width=120)

st.markdown(f"<h1 style='text-align: center;'>{weather}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>현재 공포지수(VIX): <b>{vix}</b></p>", unsafe_allow_html=True)

st.success(f"💡 **오늘의 가이드:** {advice}")

st.divider()

# 5. 추천 비중 표시
st.subheader("🚥 추천 자산 비중")
c1, c2, c3 = st.columns(3)
c1.metric("주식", f"{stock_p}%")
c2.metric("채권", f"{bond_p}%")
c3.metric("현금", f"{cash_p}%")
