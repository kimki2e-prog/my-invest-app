정말 죄송합니다! 시스템 설정이나 네트워크 환경에 따라 특정 코드 박스가 가려지는 경우가 있는 것 같습니다. 이번에는 코드 박스 형식을 완전히 배제하고, 일반 텍스트로만 코드를 길게 나열해 드릴게요.

아래의 시작 표시부터 끝 표시 전까지 모든 글자를 마우스로 긁어서 복사(Ctrl+C)한 뒤, GitHub의 app.py에 붙여넣기(Ctrl+V) 하시면 됩니다.

📥 [복사용 전체 텍스트]
--- 여기서부터 복사하세요 ---

import streamlit as st
from PIL import Image
import yfinance as yf

1. 페이지 설정 (아이콘 및 타이틀)
try:
img = Image.open("logo.png")
st.set_page_config(page_title="투자 기상청", page_icon=img, layout="centered")
except:
st.set_page_config(page_title="투자 기상청")

2. 실시간 데이터 가져오기 함수 (VIX 지수)
def get_market_data():
try:
vix_ticker = yf.Ticker("^VIX")
vix_history = vix_ticker.history(period="5d")
if not vix_history.empty:
return round(vix_history['Close'].iloc[-1], 2)
else:
return 20.0
except:
return 20.0

vix = get_market_data()

3. 데이터에 따른 상태 및 자산 비중 결정
if vix > 30:
weather_icon, weather_text, color = "⛈️", "폭풍우 (매우 위험)", "#FF4B4B"
advice = "시장이 매우 불안정합니다. 안전자산 비중을 높여 폭풍우를 피하세요."
stock, bond, cash, commodity = 20, 50, 20, 10
elif vix > 20:
weather_icon, weather_text, color = "☁️", "흐림 (주의)", "#FFA500"
advice = "변동성이 나타나고 있습니다. 무리한 공격적 투자보다는 관망이 필요합니다."
stock, bond, cash, commodity = 40, 30, 20, 10
else:
weather_icon, weather_text, color = "☀️", "맑음 (안정)", "#2E8B57"
advice = "시장이 평온한 상태입니다. 계획된 원칙에 따라 투자를 즐기세요."
stock, bond, cash, commodity = 60, 20, 10, 10

4. 화면 구성 (로고 및 날씨)
col1, col2, col3 = st.columns([1,1,1])
with col2:
try:
st.image("logo.png", width=150)
except:
st.write("이미지 로딩 중...")

st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin-bottom: 0;'>{weather_icon}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; color: {color};'>{weather_text}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>현재 실시간 공포지수(VIX): <b>{vix}</b></p>", unsafe_allow_html=True)

st.info(f"💡 가이드: {advice}")
st.divider()

5. 자산별 신호등 UI 구현
st.subheader("🚥 자산별 투자 신호등")

def signal_light_card(label, percent, color_code, icon):
st.markdown(f"""
<div style="background-color: #f8f9fb; padding: 18px; border-radius: 12px; margin-bottom: 12px; border-left: 12px solid {color_code}; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
<span style="font-size: 18px; color: #333;">{icon} <b>{label}</b></span>
<span style="float: right; font-size: 22px; color: {color_code}; font-weight: bold;">{percent}%</span>
</div>
""", unsafe_allow_html=True)

signal_light_card("주식 (위험자산)", stock, "#FF4B4B", "🔴")
signal_light_card("채권 (안전자산)", bond, "#FFA500", "🟡")
signal_light_card("현금 (대기자산)", cash, "#2E8B57", "🟢")
signal_light_card("원자재 (대체자산)", commodity, "#94a3b8", "⚪")

st.divider()
st.caption("※ 본 정보는 참고용이며, 모든 투자의 책임은 본인에게 있습니다.")
