import streamlit as st
from PIL import Image
import yfinance as yf

# 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="투자 기상청", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="투자 기상청")

# 데이터 가져오기
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

# 로직 설정
if vix > 30:
    weather_icon, weather_text, color = "⛈️", "폭풍우 (위험)", "#FF4B4B"
    advice = "안전자산 비중을 높여 폭풍우를 피하세요."
    stock, bond, cash, commodity = 20, 50, 20, 10
elif vix > 20:
    weather_icon, weather_text, color = "☁️", "흐림 (주의)", "#FFA500"
    advice = "변동성에 대비해 무리한 투자는 피하세요."
    stock, bond, cash, commodity = 40, 30, 20, 10
else:
    weather_icon, weather_text, color = "☀️", "맑음 (안정)", "#2E8B57"
    advice = "시장이 평온합니다. 원칙대로 투자하세요."
    stock, bond, cash, commodity = 60, 20, 10, 10

# 화면 UI
col1, col2, col3 = st.columns([1,1,1])
with col2:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("로고 불러오기 실패")

st.markdown(f"<h1 style='text-align: center; font-size: 80px; margin-bottom: 0;'>{weather_icon}</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; color: {color};'>{weather_text}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>변동성지수(VIX): <b>{vix}</b></p>", unsafe_allow_html=True)

st.info(f"💡 가이드: {advice}")
st.divider()

# 신호등 UI
st.subheader("🚥 자산별 투자 신호등")

def signal_light_card(label, percent, color_code, icon):
    st.markdown(f"""
        <div style="background-color: #f8f9fb; padding: 18px; border-radius: 12px; margin-bottom: 12px; border-left: 12px solid {color_code};">
            <span style="font-size: 18px;">{icon} <b>{label}</b></span>
            <span style="float: right; font-size: 22px; color: {color_code}; font-weight: bold;">{percent}%</span>
        </div>
    """, unsafe_allow_html=True)

signal_light_card("주식 (위험자산)", stock, "#FF4B4B", "🔴")
signal_light_card("채권 (안전자산)", bond, "#FFA500", "🟡")
signal_light_card("현금 (대기자산)", cash, "#2E8B57", "🟢")
signal_light_card("원자재 (대체자산)", commodity, "#94a3b8", "⚪")

st.divider()
st.caption("본 정보는 참고용이며, 모든 투자의 책임은 본인에게 있습니다.")
