import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="데이터 기반 자산관리", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="데이터 기반 자산관리")

# 2. 데이터 수집 및 계산 함수
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # [수동 업데이트]
        leading_idx = 100.5   
        export_growth = 4.6   
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. 비중 결정 상세 로직 (계산 근거 기록)
logic_details = []
stock_weight = 50 # 기본 비중

# 경기선행지수 판단
if leading_idx >= 100:
    stock_weight += 15
    logic_details.append(f"✅ **경기 확장기 (+15%):** 선행지수가 {leading_idx}로 기준치(100) 상회")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **경기 수축기 (-15%):** 선행지수가 {leading_idx}로 기준치(100) 하회")

# 수출 증가율 판단
if export_growth > 0:
    stock_weight += 15
    logic_details.append(f"✅ **수출 호조 (+15%):** 전년 대비 수출이 {export_growth}% 증가하며 코스피 하방 지지")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **수출 부진 (-15%):** 수출 성장세 둔화로 인한 국내 기업 이익 감소 우려")

# 시장 과열도(RSI) 판단
if rsi > 65:
    stock_weight -= 10
    logic_details.append(f"⚠️ **시장 과열 (-10%):** RSI가 {rsi}로 단기 고점 부담 존재")
elif rsi < 35:
    stock_weight += 10
    logic_details.append(f"✅ **과매도 구간 (+10%):** RSI가 {rsi}로 저점 매수 메리트 발생")
else:
    logic_details.append(f"ℹ️ **시장 과열도 적정 (0%):** RSI 지표가 중립 수준 유지")

# VIX 변동성 판단
if vix > 30:
    stock_weight -= 10
    logic_details.append(f"🚨 **공포 지수 급등 (-10%):** VIX가 {vix}로 시장 불안정성 매우 높음")
elif vix < 20:
    logic_details.append(f"ℹ️ **변동성 낮음 (0%):** VIX 지표가 안정적인 흐름")

stock_weight = max(10, min(95, stock_weight))

# 4. 날씨 결정
if stock_weight >= 75: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 55: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 40: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "비", "⛈️", "#FF4B4B"

# 5. UI 구성
st.markdown(f"<h1 style='text-align: center; color: {w_col};'>{w_icon} {weather}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>권장 주식 비중: {stock_weight}%</h3>", unsafe_allow_html=True)

st.divider()

# 신호등 카드 섹션
st.subheader("🚥 투자 지표 상세")
col1, col2, col3, col4 = st.columns(4)
def mini_card(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #f8f9fb; padding: 12px 5px; border-radius: 10px; border-top: 5px solid {color}; text-align: center; height: 110px;">
                <p style="color: #666; font-size: 11px; margin-bottom: 5px;">{title} 🔗</p>
                <p style="font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 14px; font-weight: bold;">{sig}</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(col1, "변동성(VIX)", vix, "안전" if vix<20 else "위험", "#2E8B57" if vix<20 else "#FF4B4B", "https://www.google.com/search?q=VIX+index")
mini_card(col2, "과열도(RSI)", rsi, "기회" if rsi<35 else "주의", "#2E8B57" if rsi<35 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI+chart")
mini_card(col3, "경기(선행)", leading_idx, "확장" if leading_idx>=100 else "수축", "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수")
mini_card(col4, "수출(한국)", f"{export_growth}%", "호조" if export_growth>0 else "부진", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=최신+수출입동향")

st.divider()

# 6. 비중 결정 근거 설명 (핵심 추가 부분!)
with st.expander("🧐 왜 이 주식 비중이 나왔나요? (계산 근거 확인)"):
    st.write("기본 주식 비중 **50%**에서 시작하여 각 지표를 평가합니다.")
    for detail in logic_details:
        st.write(detail)
    st.markdown(f"--- \n **최종 결정 비중: {stock_weight}%**")

st.progress(stock_weight / 100)
st.caption("※ 이 앱은 과거 데이터를 통한 모델이며, 모든 투자의 책임은 본인에게 있습니다.")
