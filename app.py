import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="글로벌 자산배분 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="글로벌 자산배분 전략실")

# 2. 데이터 수집 및 계산 함수
def get_market_indices():
    try:
        # VIX (실시간 변동성)
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        
        # 시장 과열도 (S&P 500 RSI)
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 경기선행지수 순환변동치 (최신 발표치 고정값)
        leading_idx = 100.5 
        
        # [신규] 수출 증가율 (전년 동월 대비 %, 최신 발표치 반영)
        # 매달 1일 산업통상자원부 발표 수치로 업데이트 하세요.
        export_growth = 4.6 
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. 개별 신호등 판별 로직
v_sig, v_col = ("안전", "#2E8B57") if vix < 20 else (("위험", "#FF4B4B") if vix > 30 else ("주의", "#FFA500"))
f_sig, f_col = ("침체(기회)", "#2E8B57") if rsi < 35 else (("과열(주의)", "#FF4B4B") if rsi > 65 else ("보통", "#FFA500"))
l_sig, l_col = ("확장", "#2E8B57") if leading_idx >= 100 else ("수축", "#FF4B4B")
# 수출 신호: 플러스(+)면 초록, 마이너스(-)면 빨강
e_sig, e_col = ("호조", "#2E8B57") if export_growth > 0 else ("부진", "#FF4B4B")

# 4. 3~6개월 중기 주식 비중 계산 로직 (가중치 업데이트)
stock_weight = 50
if leading_idx >= 100: stock_weight += 15
else: stock_weight -= 15
if export_growth > 0: stock_weight += 15 # 수출 호조 시 +15%
else: stock_weight -= 15
if rsi > 65: stock_weight -= 10
elif rsi < 35: stock_weight += 10
if vix > 30: stock_weight -= 10
stock_weight = max(10, min(95, stock_weight))

# 5. 종합 날씨 결정
if stock_weight >= 75: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 55: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 40: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "비", "⛈️", "#FF4B4B"

# 6. UI 구성
st.markdown(f"<h1 style='text-align: center; color: {w_col};'>{w_icon} {weather}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>권장 주식 비중: {stock_weight}%</h3>", unsafe_allow_html=True)

st.divider()

# 7. 지표별 신호등 (4단 구성)
st.subheader("🚥 핵심 투자 신호등 (클릭 시 상세차트)")
col1, col2, col3, col4 = st.columns(4)

def mini_card(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
            <div style="background-color: #f8f9fb; padding: 10px; border-radius: 10px; border-top: 5px solid {color}; text-align: center; cursor: pointer;">
                <small style="color: #666; font-size: 11px;">{title} 🔗</small><br>
                <span style="font-size: 16px; font-weight: bold;">{val}</span><br>
                <span style="color: {color}; font-size: 14px; font-weight: bold;">{sig}</span>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(col1, "변동성(VIX)", vix, v_sig, v_col, "https://kr.investing.com/indices/volatility-s-p-500")
mini_card(col2, "과열도(RSI)", rsi, f_sig, f_col, "https://finance.yahoo.com/quote/SPY/chart")
mini_card(col3, "경기(선행)", leading_idx, l_sig, l_col, "https://kosis.kr/visual/mainIndicators/mainIndex.do")
mini_card(col4, "수출증가율", f"{export_growth}%", e_sig, e_col, "https://www.motie.go.kr/kor/article/notification-list")

st.divider()

# 8. 자산배분 전략 대시보드
st.subheader("📅 중기 자산배분 전략")
st.progress(stock_weight / 100)

c1, c2 = st.columns(2)
with c1:
    st.metric("주식 권장 비중", f"{stock_weight}%")
    st.metric("현금/채권 비중", f"{100 - stock_weight}%")
with c2:
    if stock_weight >= 70:
        st.success("🟢 경기와 수출이 모두 긍정적입니다. 적극적인 투자가 유리합니다.")
    elif stock_weight >= 40:
        st.warning("🟡 지표가 엇갈리고 있습니다. 돌발 변수에 대비한 분할 대응을 권장합니다.")
    else:
        st.error("🔴 경기 하강 및 수출 부진 구간입니다. 안전 자산 확보에 집중하세요.")

st.caption("※ 수출증가율은 산업통상자원부의 전년 동월 대비 증감률 데이터를 기준으로 합니다.")
