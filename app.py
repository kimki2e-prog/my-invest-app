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
        vix_data = yf.Ticker("^VIX").history(period="1d")
        vix = vix_data['Close'].iloc[-1]
        
        # 공포탐욕 대용 (RSI)
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 경기선행지수 순환변동치 (최근 발표치 - 매달 말 업데이트 권장)
        leading_idx = 100.5 
        
        return round(vix, 2), round(rsi, 2), leading_idx
    except:
        return 20.0, 50.0, 100.0

vix, rsi, leading_idx = get_market_indices()

# 3. 개별 신호등 판별
v_sig, v_col = ("안전", "#2E8B57") if vix < 20 else (("위험", "#FF4B4B") if vix > 30 else ("주의", "#FFA500"))
f_sig, f_col = ("기회", "#2E8B57") if rsi < 35 else (("과열", "#FF4B4B") if rsi > 65 else ("보통", "#FFA500"))
l_sig, l_col = ("확장", "#2E8B57") if leading_idx >= 100 else ("수축", "#FF4B4B")

# 4. 3~6개월 중기 주식 비중 계산 로직
stock_weight = 50
if leading_idx >= 100: stock_weight += 20
else: stock_weight -= 20
if rsi > 65: stock_weight -= 10
elif rsi < 35: stock_weight += 10
if vix > 30: stock_weight -= 10
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

# 지표별 신호등 및 링크 섹션 (수정된 링크 반영)
st.subheader("🚥 현재 시장 신호등 (클릭 시 상세차트)")
col1, col2, col3 = st.columns(3)

def mini_card_with_link(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
            <div style="background-color: #f8f9fb; padding: 10px; border-radius: 10px; border-top: 5px solid {color}; text-align: center; cursor: pointer;">
                <small style="color: #666;">{title} 🔗</small><br>
                <span style="font-size: 18px; font-weight: bold;">{val}</span><br>
                <span style="color: {color}; font-weight: bold;">{sig}</span>
            </div>
        </a>
    """, unsafe_allow_html=True)

# 🔗 수정된 링크 주소들
# 1. VIX: 인베스팅닷컴이 한글 지원 및 차트가 깔끔합니다.
vix_link = "https://kr.investing.com/indices/volatility-s-p-500"
# 2. 공포탐욕: CNN 공식 페이지
fear_link = "https://edition.cnn.com/markets/fear-and-greed"
# 3. 경기선행지수: 통계청(KOSIS) 국가통계포털 메인 지표 페이지 (가장 정확함)
leading_link = "https://kosis.kr/visual/mainIndicators/mainIndex.do"

mini_card_with_link(col1, "변동성(VIX)", vix, v_sig, v_col, vix_link)
mini_card_with_link(col2, "심리(Greed)", rsi, f_sig, f_col, fear_link)
mini_card_with_link(col3, "경기(선행)", leading_idx, l_sig, l_col, leading_link)

st.divider()

# 자산배분 전략 대시보드
st.subheader("📅 3~6개월 자산배분 전략")
st.progress(stock_weight / 100)

c1, c2 = st.columns(2)
with c1:
    st.metric("주식 권장 비중", f"{stock_weight}%")
    st.metric("현금/채권 비중", f"{100 - stock_weight}%")
with c2:
    if stock_weight >= 70:
        st.success("🟢 경기 확장기입니다. 공격적 포트폴리오를 권장합니다.")
    elif stock_weight >= 40:
        st.warning("🟡 중립 구간입니다. 분할 매수/매도로 대응하세요.")
    else:
        st.error("🔴 경기 수축기입니다. 자산 방어에 집중하세요.")

st.caption("※ 지표 카드를 클릭하면 공식 통계 및 실시간 차트 페이지로 연결됩니다.")
