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

# 3. 중기 비중 결정 상세 로직 (가중치 설정)
logic_details = []
stock_weight = 50 # 기본 비중 50% 시작

# 경기(선행지수) - 중기 방향성의 핵심
if leading_idx >= 100:
    stock_weight += 15
    logic_details.append(f"✅ **경기 확장 국면 (+15%):** 선행지수({leading_idx})가 기준선 상회 중")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **경기 수축 국면 (-15%):** 선행지수({leading_idx})가 기준선 하회 중")

# 한국 수출 - 코스피의 선행지표
if export_growth > 0:
    stock_weight += 15
    logic_details.append(f"✅ **수출 성장세 (+15%):** 한국 수출 증가율({export_growth}%) 플러스 유지")
else:
    stock_weight -= 15
    logic_details.append(f"⚠️ **수출 역성장 (-15%):** 한국 수출 증가율({export_growth}%) 마이너스 기록")

# 시장 과열도(RSI) - 중기적 고점/저점 판단
if rsi > 65:
    stock_weight -= 10
    logic_details.append(f"⚠️ **중기 고점 부담 (-10%):** RSI({rsi}) 기준 시장 과열 신호 발생")
elif rsi < 35:
    stock_weight += 10
    logic_details.append(f"✅ **중기 저점 매력 (+10%):** RSI({rsi}) 기준 과매도 구간 진입")
else:
    logic_details.append(f"ℹ️ **시장 심리 중립 (0%):** 과열이나 침체 없는 적정 수준")

# 변동성(VIX) - 위험 관리 지표
if vix > 30:
    stock_weight -= 20
    logic_details.append(f"🚨 **시장 패닉 발생 (-20%):** VIX({vix}) 급등으로 안전자산 선호 강화")
elif vix > 22:
    stock_weight -= 10
    logic_details.append(f"🟡 **변동성 확대 (-10%):** VIX({vix}) 상승으로 리스크 관리 필요")
else:
    logic_details.append(f"✅ **변동성 안정 (0%):** VIX({vix})가 낮아 투자 심리 평온")

stock_weight = max(10, min(95, stock_weight))
safe_weight = 100 - stock_weight

# 4. 종합 날씨 결정
if stock_weight >= 75: weather, w_icon, w_col = "매우 맑음", "☀️", "#2E8B57"
elif stock_weight >= 55: weather, w_icon, w_col = "구름 조금", "🌤️", "#3CB371"
elif stock_weight >= 40: weather, w_icon, w_col = "흐림", "☁️", "#FFA500"
else: weather, w_icon, w_col = "폭풍우", "⛈️", "#FF4B4B"

# 5. [최상단] 오늘의 투자 날씨
st.markdown(f"<div style='text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 20px; margin-bottom: 25px;'> <p style='font-size: 20px; margin-bottom: 5px; color: #555;'>오늘의 종합 투자 날씨</p> <h1 style='font-size: 60px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1> </div>", unsafe_allow_html=True)

# 6. 중기 자산배분 신호등 (강조 섹션)
st.subheader("🚥 향후 3~6개월 자산배분 전략")
col_stock, col_safe = st.columns(2)

with col_stock:
    st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 25px; border-radius: 15px; border: 4px solid #2E8B57; text-align: center;">
            <h3 style="color: #2E8B57; margin: 0;">주식 비중</h3>
            <h1 style="font-size: 55px; margin: 10px 0; color: #1b5e20;">{stock_weight}%</h1>
            <p style="color: #4caf50; font-weight: bold;">[공격/성장 자산]</p>
        </div>
    """, unsafe_allow_html=True)

with col_safe:
    st.markdown(f"""
        <div style="background-color: #ffebee; padding: 25px; border-radius: 15px; border: 4px solid #FF4B4B; text-align: center;">
            <h3 style="color: #FF4B4B; margin: 0;">안전자산 비중</h3>
            <h1 style="font-size: 55px; margin: 10px 0; color: #b71c1c;">{safe_weight}%</h1>
            <p style="color: #f44336; font-weight: bold;">[방어/현금 자산]</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 7. 세부 지표 현황
st.subheader("🔍 주요 시장 지표")
c1, c2, c3, c4 = st.columns(4)
def mini_card(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffffff; padding: 12px 5px; border-radius: 10px; border: 1px solid #ddd; border-top: 5px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 11px; margin:0;">{title} 🔗</p>
                <p style="font-size: 16px; font-weight: bold; margin:5px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 14px; font-weight: bold; margin:0;">{sig}</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

mini_card(c1, "변동성(VIX)", vix, "안전" if vix<22 else "위험", "#2E8B57" if vix<22 else "#FF4B4B", "https://www.google.com/search?q=VIX+index")
mini_card(c2, "시장과열(RSI)", rsi, "기회" if rsi<40 else "주의", "#2E8B57" if rsi<40 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI")
mini_card(c3, "경기(선행)", leading_idx, "확장" if leading_idx>=100 else "수축", "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수")
mini_card(c4, "한국수출", f"{export_growth}%", "호조" if export_growth>0 else "부진", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=최신+수출입동향")

st.divider()

# 8. 비중 결정 상세 근거 (Expander)
with st.expander("🧐 자산배분 결정 근거 (중기 전략)"):
    st.write("중기 포트폴리오의 기본 주식 비중 **50%**를 기준으로 산출되었습니다.")
    for detail in logic_details:
        st.write(detail)
    st.markdown(f"--- \n **최종 중기 권장 비중: 주식 {stock_weight}% / 안전자산 {safe_weight}%**")

st.caption("※ 본 앱은 투자 참고용이며, 최종 투자 판단의 책임은 사용자 본인에게 있습니다.")
