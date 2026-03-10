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
        
        # [수동 업데이트] 매달 발표되는 뉴스를 보고 아래 숫자만 수정하세요!
        leading_idx = 100.5   # 경기선행지수 순환변동치 (100 기준)
        export_growth = 4.6   # 수출 증가율 (%) (0 기준)
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. 신호등 판별 및 색상 설정
v_sig, v_col = ("안전", "#2E8B57") if vix < 20 else (("위험", "#FF4B4B") if vix > 30 else ("주의", "#FFA500"))
f_sig, f_col = ("침체(기회)", "#2E8B57") if rsi < 35 else (("과열(주의)", "#FF4B4B") if rsi > 65 else ("보통", "#FFA500"))
l_sig, l_col = ("확장", "#2E8B57") if leading_idx >= 100 else ("수축", "#FF4B4B")
e_sig, e_col = ("호조", "#2E8B57") if export_growth > 0 else ("부진", "#FF4B4B")

# 4. 주식 비중 계산
stock_weight = 50
if leading_idx >= 100: stock_weight += 15
else: stock_weight -= 15
if export_growth > 0: stock_weight += 15
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

# 7. [수정] 오류 없는 '검색 기반' 링크 연결
st.subheader("🚥 투자 지표 상세 확인 (클릭)")
col1, col2, col3, col4 = st.columns(4)

def mini_card(col, title, val, sig, color, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #f8f9fb; padding: 12px 5px; border-radius: 10px; border-top: 5px solid {color}; text-align: center; height: 120px;">
                <p style="color: #666; font-size: 11px; margin-bottom: 5px;">{title} 🔗</p>
                <p style="font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 14px; font-weight: bold;">{sig}</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

# 🔗 2026년 기준 가장 안 깨지는 링크 (구글 검색 활용)
vix_url = "https://www.google.com/search?q=VIX+index"
rsi_url = "https://www.google.com/search?q=SPY+RSI+chart" 
leading_url = "https://www.google.com/search?q=경기선행지수+순환변동치+추이"
export_url = "https://www.google.com/search?q=최신+수출입동향+보도자료" # <--- 구글 검색으로 교체!

mini_card(col1, "변동성(VIX)", vix, v_sig, v_col, vix_url)
mini_card(col2, "과열도(RSI)", rsi, f_sig, f_col, rsi_url)
mini_card(col3, "경기(선행)", leading_idx, l_sig, l_col, leading_url)
mini_card(col4, "수출증가율", f"{export_growth}%", e_sig, e_col, export_url)

st.divider()

# 8. 자산배분 가이드
st.subheader("📅 중기 자산배분 가이드")
st.progress(stock_weight / 100)

c1, c2 = st.columns(2)
with c1:
    st.metric("주식 권장 비중", f"{stock_weight}%")
    st.metric("현금/채권 비중", f"{100 - stock_weight}%")
with c2:
    if stock_weight >= 70: st.success("🟢 지표가 우호적입니다. 공격적 투자가 가능한 시기입니다.")
    elif stock_weight >= 40: st.warning("🟡 지표가 혼조세입니다. 리스크 관리를 병행하세요.")
    else: st.error("🔴 방어적인 태세가 필요합니다. 안전자산을 확보하세요.")

st.caption("※ 각 지표 카드를 클릭하면 최신 데이터 검색 결과로 이동합니다.")
