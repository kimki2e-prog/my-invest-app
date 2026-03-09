import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정 (브라우저 탭 아이콘 및 제목)
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="투자 기상청", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="투자 기상청")

# 2. 실시간 데이터 가져오기 함수 (VIX 지수)
def get_market_data():
    try:
        vix_ticker = yf.Ticker("^VIX")
        vix_history = vix_ticker.history(period="5d") # 안전하게 5일치 확보
        if not vix_history.empty:
            return round(vix_history['Close'].iloc[-1], 2)
        else:
            return 20.0
    except:
        return 20.0

vix = get_market_data()

# 3. 데이터에 따른 날씨 및 자산 비중 결정 로직
if vix > 30:
    weather_icon = "⛈️"
    weather_text = "폭풍우 (매우 위험)"
    bg_color = "#FF4B4B" # 빨간색 계열
    advice = "시장이 매우 불안정합니다. 현금 비중을 최대한 확보하고 관망하세요."
    stock, bond, cash, commodity = 20, 50, 20, 10
elif vix > 20:
    weather_icon = "☁️"
    weather_text = "흐림 (주의)"
    bg_color = "#FFA500" # 주황색 계열
    advice = "변동성이 커지고 있습니다. 무리한 투자는 피하고 자산 배분을 점검하세요."
    stock, bond, cash, commodity = 40, 30, 20, 10
else:
    weather_icon = "☀️"
    weather_text = "맑음 (안정)"
    bg_color = "#2E8B57" # 초록색 계열
    advice = "시장이 평온합니다. 정해진 계획에 따라 포트폴리오를 유지하세요."
    stock, bond, cash, commodity = 60, 20, 10, 10

# 4. 화면 UI 구성 (첫 번째 디자인 스타일)
# 상단 로고 중앙 배치
col1, col2, col3 = st.columns([1,1,1])
with col2:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("이미지 로딩 중...")

# 날씨 및 지수 표시
st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin-bottom: 0;'>{weather_icon}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; color: {bg_color};'>{weather_text}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>실시간 공포지수(VIX): <b>{vix}</b></p>", unsafe_allow_html=True)

# 가이드 박스
st.info(f"💡 **오늘의 투자 가이드:** {advice}")

st.divider()

# 자산 배분 신호등 (숫자 위주 대시보드)
st.subheader("🚥 추천 자산 배분")
c1, c2, c3, c4 = st.columns(4)
c1.metric("주식", f"{stock}%")
c2.metric("채권", f"{bond}%")
c3.metric("현금", f"{cash}%")
c4.metric("원자재", f"{commodity}%")

st.divider()
st.caption("데이터 출처: Yahoo Finance (VIX Index 기준)")
