import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="중기 투자 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="중기 투자 전략실")

# 2. 데이터 수집 함수
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # [수동 업데이트 구간] 매달 발표치를 확인하여 수정하세요.
        leading_idx = 100.5   # 경기선행지수 순환변동치
        export_growth = 4.6   # 한국 수출 증가율 (%)
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. [수정] 중기 비중 결정 로직 (기본 비중 25% 시작)
logic_details = []
stock_weight = 25 # 요청하신 대로 기본 비중을 25%로 설정했습니다.

# 경기(선행지수) 
if leading_idx >= 100:
    stock_weight += 20
    logic_details.append(f"✅ **경기 확장기 (+20%):** 선행지수({leading_idx}) 기준선 상회")
else:
    stock_weight -= 10
    logic_details.append(f"⚠️ **경기 수축기 (-10%):** 선행지수({leading_idx}) 기준선 하회")

# 한국 수출
if export_growth > 0:
    stock_weight += 20
    logic_details.append(f"✅ **수출 호조 (+20%):** 한국 수출 증가율({export_growth}%) 플러스")
else:
    stock_weight -= 10
    logic_details.append(f"⚠️ **수출 부진 (-10%):** 한국 수출 증가율({export_growth}%) 마이너스")

# 시장 과열도(RSI)
if rsi > 65:
    stock_weight -= 10
    logic_details.append(f"⚠️ **중기 고점 부담 (-10%):** RSI({rsi}) 과열 신호")
elif rsi < 35:
    stock_weight += 15
    logic_details.append(f"✅ **중기 저점 매력 (+15%):** RSI({rsi}) 과매도 구간")

# 변동성(VIX)
if vix > 25:
    stock_weight -= 15
    logic_details.append(f"🚨 **변동성 확대 (-15%):** VIX({vix}) 상승으로 위험 회피 필요")
elif vix < 15:
    stock_weight += 5
    logic_details.append(f"✅ **시장 안정 (+5%):** VIX({vix})가 매우 낮아 평온한 상태")

# 최종 비중 제한 (5% ~ 95%)
stock_weight = max(5, min(95, stock_weight))
safe_weight = 100 - stock_weight

# 4. 날씨 결정
if stock_weight >= 70: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 45: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 25: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "폭풍우", "⛈️", "#FF4B4B"

# 5. [최상단] 오늘의 종합 투자 날씨
st.markdown(f"""
    <div style='text-align: center; background-color: #f8f9fa; padding: 30px; border-radius: 25px; border: 1px solid #eee; margin-bottom: 30px;'>
        <p style='font-size: 18px; color: #666; margin-bottom: 5px;'>중기 투자 기상도</p>
        <h1 style='font-size: 60px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1>
    </div>
""", unsafe_allow_html=True)

# 6. 중기 자산배분 전략 카드
st.subheader("🚥 향후 3~6개월 자산배분 전략")
c_stock, c_safe = st.columns(2)
with c_stock:
    st.markdown(f"<div style='background-color: #e8f5e9; padding: 25px; border-radius: 15px; border: 4px solid #2E8B57; text-align: center;'><h3 style='color: #2E8B57; margin:0;'>주식 비중</h3><h1 style='font-size: 55px; color: #1b5e20; margin:10px 0;'>{stock_weight}%</h1></div>", unsafe_allow_html=True)
with c_safe:
    st.markdown(f"<div style='background-color: #ffebee; padding: 25px; border-radius: 15px; border: 4px solid #FF4B4B; text-align: center;'><h3 style='color: #FF4B4B; margin:0;'>안전 자산</h3><h1 style='font-size: 55px; color: #b71c1c; margin:10px 0;'>{safe_weight}%</h1></div>", unsafe_allow_html=True)

st.divider()

# 7. [강조] 클릭을 유도하는 인터랙티브 지표 카드
st.subheader("🔍 주요 시장 지표 (자세히 보려면 클릭 🔗)")

# 마우스 오버 효과 CSS
st.markdown("""
    <style>
    .indicator-card {
        background-color: #ffffff;
        padding: 15px 5px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none !important;
        display: block;
    }
    .indicator-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: #007bff;
        background-color: #f0f7ff;
    }
    .indicator-title { color: #555; font-size: 12px; margin-bottom: 8px; font-weight: bold; }
    .indicator-value { font-size: 18px; font-weight: 800; color: #222; margin-bottom: 4px; }
    .indicator-sig { font-size: 14px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

def link_card(col, title, val, sig, color, url):
    col.markdown(f"""
        <a href="{url}" target="_blank" class="indicator-card" style="border-top: 6px solid {color};">
            <div class="indicator-title">{title} 🔗</div>
            <div class="indicator-value">{val}</div>
            <div class="indicator-sig" style="color: {color};">{sig}</div>
        </a>
    """, unsafe_allow_html=True)

link_card(col1, "변동성 VIX", vix, "안전" if vix<22 else "위험", "#2E8B57" if vix<22 else "#FF4B4B", "https://www.google.com/search?q=VIX+index+chart")
link_card(col2, "과열도 RSI", rsi, "기회" if rsi<40 else "주의", "#2E8B57" if rsi<40 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI+indicator")
link_card(col3, "경기 선행", leading_idx, "확장" if leading_idx>=100 else "수축", "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수+순환변동치")
link_card(col4, "한국 수출", f"{export_growth}%", "호조" if export_growth>0 else "부진", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=최신+수출입동향+보도자료")

st.divider()

# 8. 자산배분 근거 (Expander)
with st.expander("🧐 자산배분 결정 근거 확인하기"):
    st.write(f"본 모델은 기본 주식 비중 **25%**에서 시작하여 시장 상황에 따라 비중을 조절합니다.")
    for d in logic_details: st.write(d)
    st.info(f"종합적인 중기 분석 결과, **주식 {stock_weight}% / 안전자산 {safe_weight}%** 배분을 권장합니다.")

st.caption("※ 지표 카드를 클릭하면 상세 데이터 검색 결과 페이지로 연결됩니다.")
