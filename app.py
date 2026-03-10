import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="4대 자산 배분 전략실", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="4대 자산 배분 전략실", layout="wide")

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

# 3. [세분화 로직] 자산별 비중 계산
# 초기값 설정 (기본 주식 비중 25% 기준)
stock_w = 25
bond_w = 40
gold_w = 20
cash_w = 15

logic_details = []

# [지표 1] 경기 & 수출 (성장 지표 -> 주식 비중 결정)
if leading_idx >= 100 and export_growth > 0:
    stock_w += 25
    bond_w -= 10
    logic_details.append("✅ **경기 확장 & 수출 호조:** 주식 비중을 대폭 확대하고 채권 비중을 축소합니다.")
elif leading_idx < 100 and export_growth < 0:
    stock_w -= 15
    bond_w += 15
    cash_w += 5
    logic_details.append("⚠️ **경기 수축 & 수출 부진:** 주식 비중을 줄이고 채권 및 현금 비중을 늘려 방어합니다.")

# [지표 2] 변동성 VIX (위험 지표 -> 금 & 현금 비중 결정)
if vix > 25:
    gold_w += 10
    stock_w -= 10
    logic_details.append(f"🚨 **시장 불안 고조 (VIX {vix}):** 안전자산인 금(원자재) 비중을 높입니다.")
elif vix < 15:
    gold_w -= 5
    stock_w += 5
    logic_details.append(f"✅ **시장 안정기 (VIX {vix}):** 금 비중을 줄이고 공격 자산을 늘립니다.")

# [지표 3] 과열도 RSI (심리 지표 -> 현금 비중 결정)
if rsi > 65:
    cash_w += 10
    stock_w -= 10
    logic_details.append(f"⚠️ **시장 과열 (RSI {rsi}):** 현금 비중을 확보하여 조정에 대비합니다.")
elif rsi < 35:
    cash_w -= 5
    stock_w += 10
    logic_details.append(f"✅ **과매도 구간 (RSI {rsi}):** 현금을 사용해 주식 저가 매수를 진행합니다.")

# 최종 비중 정규화 (합계 100 유지)
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100)
cash_w = 100 - (stock_w + bond_w + gold_w)

# 4. 종합 투자 날씨 결정
if stock_w >= 50: weather, w_icon, w_col = "공격적 확장", "☀️", "#2E8B57"
elif stock_w >= 30: weather, w_icon, w_col = "중립적 유지", "🌤️", "#3CB371"
else: weather, w_icon, w_col = "보수적 방어", "⛈️", "#FF4B4B"

# 5. UI 구성 - 상단 날씨
st.markdown(f"""
    <div style='text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 20px;'>
        <p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p>
        <h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1>
    </div>
""", unsafe_allow_html=True)

# 6. [핵심] 4대 자산 배분 신호등
st.subheader("🚥 중기 자산별 권장 비중")
col1, col2, col3, col4 = st.columns(4)

def asset_card(col, title, weight, color, desc):
    col.markdown(f"""
        <div style="background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center; height: 160px;">
            <h4 style="color: {color}; margin: 0;">{title}</h4>
            <h1 style="font-size: 40px; color: {color}; margin: 10px 0;">{weight}%</h1>
            <p style="font-size: 12px; color: #666; margin: 0;">{desc}</p>
        </div>
    """, unsafe_allow_html=True)

asset_card(col1, "주식", stock_w, "#2E8B57", "성장 자산 (ETF/개별)")
asset_card(col2, "채권", bond_w, "#007BFF", "수익률 방어 (국채)")
asset_card(col3, "금/원자재", gold_w, "#FFD700", "인플레/위험 헤지")
asset_card(col4, "현금", cash_w, "#6C757D", "유동성/기회 포착")

st.divider()

# 7. 시장 지표 인터랙티브 카드
st.subheader("🔍 주요 시장 지표 (클릭 시 상세 정보 🔗)")
st.markdown("""
    <style>
    .indicator-card {
        background-color: #ffffff; padding: 12px; border-radius: 10px; border: 1px solid #ddd;
        text-align: center; transition: all 0.2s; cursor: pointer; text-decoration: none !important; display: block;
    }
    .indicator-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-color: #007bff; }
    </style>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
def link_card(col, title, val, color, url):
    col.markdown(f"""
        <a href="{url}" target="_blank" class="indicator-card" style="border-top: 5px solid {color};">
            <div style="font-size: 11px; color: #777;">{title} 🔗</div>
            <div style="font-size: 18px; font-weight: bold; color: #333;">{val}</div>
        </a>
    """, unsafe_allow_html=True)

link_card(m1, "변동성 VIX", vix, "#2E8B57" if vix<22 else "#FF4B4B", "https://www.google.com/search?q=VIX+index")
link_card(m2, "과열도 RSI", rsi, "#2E8B57" if rsi<40 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI")
link_card(m3, "경기 선행", leading_idx, "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수")
link_card(m4, "한국 수출", f"{export_growth}%", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 자산배분 근거 (Expander)
with st.expander("🧐 세부 자산배분 결정 근거 보기"):
    st.write(f"기본 주식 비중 **25%**를 기준으로 4대 자산의 상관관계를 분석한 결과입니다.")
    for d in logic_details:
        st.write(d)
    st.info(f"이 포트폴리오는 시장의 변동성을 금과 채권으로 방어하면서, 경기 회복 시 주식 수익률을 극대화하도록 설계되었습니다.")

st.caption("※ 본 데이터는 투자 참고용이며 최종 판단은 투자자 본인에게 있습니다.")
