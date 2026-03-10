import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="스마트 자산배분 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="스마트 자산배분 전략실")

# 2. 데이터 수집 함수
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # [수동 업데이트 구간]
        leading_idx = 100.5   
        export_growth = 4.6   
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. 비중 결정 상세 로직 (변동성 포함)
logic_details = []
stock_weight = 50 # 기본 비중 시작

# [지표 1] 경기선행지수
if leading_idx >= 100:
    stock_weight += 15
    logic_details.append(f"✅ **경기 확장기 (+15%):** 선행지수({leading_idx})가 기준치 상회")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **경기 수축기 (-15%):** 선행지수({leading_idx})가 기준치 하회")

# [지표 2] 수출 증가율
if export_growth > 0:
    stock_weight += 15
    logic_details.append(f"✅ **수출 호조 (+15%):** 한국 수출 증가율({export_growth}%) 양호")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **수출 부진 (-15%):** 한국 수출 증가율({export_growth}%) 마이너스")

# [지표 3] 시장 과열도(RSI)
if rsi > 65:
    stock_weight -= 10
    logic_details.append(f"⚠️ **시장 과열 (-10%):** RSI({rsi})가 고점 부담 영역 진입")
elif rsi < 35:
    stock_weight += 10
    logic_details.append(f"✅ **과매도 구간 (+10%):** RSI({rsi})가 저가 매수 매력 발생")
else:
    logic_details.append(f"ℹ️ **시장 심리 적정 (0%):** RSI 지표가 중립 수준")

# [지표 4] 변동성(VIX) - 누락되었던 부분 보강
if vix > 30:
    stock_weight -= 20
    logic_details.append(f"🚨 **고변동성 위기 (-20%):** VIX({vix}) 급등으로 시장 패닉 상태")
elif vix > 22:
    stock_weight -= 10
    logic_details.append(f"🟡 **변동성 확대 (-10%):** VIX({vix})가 상승하며 불안 심리 확산")
else:
    logic_details.append(f"✅ **변동성 안정 (0%):** VIX({vix})가 낮아 평온한 시장 유지")

stock_weight = max(10, min(95, stock_weight))
safe_weight = 100 - stock_weight

# 4. 날씨 결정
if stock_weight >= 75: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 55: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 40: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "비", "⛈️", "#FF4B4B"

# 5. 상단 날씨 UI
st.markdown(f"<h1 style='text-align: center; color: {w_col};'>{w_icon} {weather}</h1>", unsafe_allow_html=True)
st.divider()

# 6. 주식 vs 안전자산 비중 신호등 (강조 섹션)
st.subheader("🚥 실시간 자산배분 신호등")
col_stock, col_safe = st.columns(2)

with col_stock:
    st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 15px; border: 3px solid #2E8B57; text-align: center;">
            <h2 style="color: #2E8B57; margin: 0;">주식 비중</h2>
            <h1 style="font-size: 50px; margin: 10px 0;">{stock_weight}%</h1>
            <p style="color: #666;">위험자산 공격형 투자</p>
        </div>
    """, unsafe_allow_html=True)

with col_safe:
    st.markdown(f"""
        <div style="background-color: #ffebee; padding: 20px; border-radius: 15px; border: 3px solid #FF4B4B; text-align: center;">
            <h2 style="color: #FF4B4B; margin: 0;">안전자산 비중</h2>
            <h1 style="font-size: 50px; margin: 10px 0;">{safe_weight}%</h1>
            <p style="color: #666;">현금·채권 방어형 투자</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. 지표별 4분할 신호등
st.subheader("🔍 세부 지표 현황")
c1, c2, c3, c4 = st.columns(4)
def mini_card(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #f8f9fb; padding: 10px; border-radius: 10px; border-top: 5px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 11px; margin:0;">{title} 🔗</p>
                <p style="font-size: 16px; font-weight: bold; margin:5px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 14px; font-weight: bold; margin:0;">{sig}</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(c1, "변동성(VIX)", vix, "안전" if vix<22 else "위험", "#2E8B57" if vix<22 else "#FF4B4B", "https://www.google.com/search?q=VIX+index")
mini_card(c2, "과열도(RSI)", rsi, "기회" if rsi<40 else "주의", "#2E8B57" if rsi<40 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI")
mini_card(c3, "경기(선행)", leading_idx, "확장" if leading_idx>=100 else "수축", "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수")
mini_card(c4, "수출(한국)", f"{export_growth}%", "호조" if export_growth>0 else "부진", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=최신+수출입동향")

st.divider()

# 8. 계산 근거 (Expander)
with st.expander("🧐 비중 결정 상세 근거 보기"):
    st.write("기본 주식 비중 **50%**를 기준으로 현재 지표들을 평가한 결과입니다.")
    for detail in logic_details:
        st.write(detail)
    st.markdown(f"--- \n **최종 권장 주식 비중: {stock_weight}%**")

st.caption("※ 본 앱은 투자 참고용이며, 최종 투자 판단의 책임은 본인에게 있습니다.")
