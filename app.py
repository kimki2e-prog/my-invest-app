import streamlit as st
import pandas as pd

# 1. 앱 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="투자 기상청", layout="centered")

# 2. 가상의 지표 데이터 (실제 서비스 시 API 연동)
vix = 22.5
fear_greed = 35
cli_trend = "down" # 경기선행지수 하락 중

# 3. 자산 배분 로직 (앞서 만든 로직 적용)
def get_allocation(vix, fg, cli):
    # 단순화된 로직 예시
    if fg < 30 and cli == "down":
        return {"날씨": "⛈️ 폭풍우", "색상": "#4A4A4A", "주식": 20, "채권": 50, "현금": 20, "원자재": 10}
    elif fg > 70:
        return {"날씨": "☀️ 폭염(과열)", "색상": "#FF4B4B", "주식": 30, "채권": 30, "현금": 35, "원자재": 5}
    else:
        return {"날씨": "🌤️ 구름조금", "색상": "#00AEEF", "주식": 50, "채권": 30, "현금": 10, "원자재": 10}

data = get_allocation(vix, fear_greed, cli_trend)

# 4. UI 렌더링
st.title("🌡️ 오늘의 투자 기상도")
st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{data['날씨']}</h1>", unsafe_allow_html=True)
st.info(f"현재 시장은 **'{data['날씨']}'** 상태입니다. 안전 자산 비중을 점검하세요.")

st.divider()

# 5. 자산별 신호등 UI
st.subheader("🚥 자산별 투자 신호등")
cols = st.columns(2)

assets = [
    ("주식", data['주식'], "🔴 위험"),
    ("채권", data['채권'], "🟡 주의"),
    ("현금", data['현금'], "🟢 안전"),
    ("원자재", data['원자재'], "⚪ 중립")
]

for i, (name, percent, status) in enumerate(assets):
    with cols[i % 2]:
        st.metric(label=name, value=f"{percent}%", delta=status)

st.divider()

# 6. 행동 가이드
st.warning("💡 **Action Plan:** 현재 주식 비중을 낮추고 현금을 확보하여 다음 기회를 기다릴 때입니다.")
