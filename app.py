import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="중기 4대 자산전략실", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="중기 4대 자산전략실", layout="wide")

# 2. 데이터 수집
def get_market_indices():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # [수동 업데이트] 2026년 발표치 기준
        leading_idx = 100.5   # 경기선행지수
        export_growth = 4.6   # 한국 수출 증가율
        
        return round(vix, 2), round(rsi, 2), leading_idx, export_growth
    except:
        return 20.0, 50.0, 100.0, 0.0

vix, rsi, leading_idx, export_growth = get_market_indices()

# 3. 자산별 비중 계산 (기본 주식 25% -> 공격적 가산점 적용)
stock_w, bond_w, gold_w, cash_w = 25, 40, 20, 15

# [공격적 조정] 지표별 상태 및 비중 가감
if vix > 25: vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "안전자산 확보"; gold_w += 10; stock_w -= 15
elif vix < 15: vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "주식 적극 확대"; gold_w -= 5; stock_w += 15 # +5에서 +15로 상향
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "중립 유지"; 

if rsi > 65: rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "현금 비중 확보"; cash_w += 10; stock_w -= 10
elif rsi < 35: rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "적극 저가 매수"; cash_w -= 10; stock_w += 20 # +10에서 +20으로 상향
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "가격 적정 수준"; 

if leading_idx >= 100: eco_sig, eco_col, eco_desc = "확장", "#2E8B57", "경기 주도주 확대"; stock_w += 20; bond_w -= 10 # +15에서 +20으로 상향
else: eco_sig, eco_col, eco_desc = "수축", "#FF4B4B", "방어 자산 확대"; stock_w -= 10; bond_w += 15

if export_growth > 0: exp_sig, exp_col, exp_desc = "호조", "#2E8B57", "수익 극대화 전략"; stock_w += 15; gold_w -= 5 # +10에서 +15로 상향
else: exp_sig, exp_col, exp_desc = "부진", "#FF4B4B", "보수적 대응"; stock_w -= 15; cash_w += 10

# 비중 정규화 및 주식 최소 30% 강제 보정
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
if stock_w < 30:
    diff = 30 - stock_w
    stock_w = 30
    bond_w -= diff 

bond_w = round((bond_w / (bond_w+gold_w+cash_w)) * (100-stock_w))
gold_w = round((gold_w / (bond_w+gold_w+cash_w)) * (100-stock_w))
cash_w = 100 - (stock_w + bond_w + gold_w)

# 4. 날씨 결정
if stock_w >= 65: weather, w_icon, w_col = "적극적 공격", "🔥", "#2E8B57" # 아이콘 변경 및 기준 상향
elif stock_w >= 45: weather, w_icon, w_col = "안정적 확장", "☀️", "#3CB371"
elif stock_w >= 30: weather, w_icon, w_col = "보수적 방어", "☁️", "#FFA500"
else: weather, w_icon, w_col = "위기 관리", "⛈️", "#FF4B4B"

# 5. UI - 상단 기상도
st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 25px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p><h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
st.subheader("🚥 자산별 권장 비중 (공격적 비중 반영)")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 통합 분석
st.subheader("🔍 핵심 지표 통합 분석 (클릭 시 상세 정보 🔗)")

def mini_card(col, title, val, sig, color, desc, link):
    col.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;">
                <p style="color: #666; font-size: 12px; margin:0; font-weight: bold;">{title} 🔗</p>
                <p style="font-size: 20px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p>
                <p style="color: {color}; font-size: 15px; font-weight: bold; margin:0;">{sig} ({desc})</p>
            </div>
        </a>
    """, unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
mini_card(m1, "공포 지수 (VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
mini_card(m2, "과열도 (RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")
mini_card(m3, "경기 선행 (지수)", leading_idx, eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수")
mini_card(m4, "한국 수출 (증가율)", f"{export_growth}%", exp_sig, exp_col, exp_desc, "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 자산배분 전략 상세 가이드
st.subheader("📑 자산배분 전략 상세 가이드")
with st.expander("📚 이 포트폴리오는 어떤 원리로 결정되나요? (상세 설명 보기)", expanded=True):
    st.markdown("""
    본 앱의 알고리즘은 **'매크로 지표'**와 **'시장 심리'**를 결합하여 자산별 최적 비중을 도출합니다.
    
    ### 1. 주식 (Growth Asset) - 최소 비중 30%
    * **결정 원리:** 한국 수출 증가율과 경기선행지수가 주가 상승의 핵심 동력입니다. 두 지표가 모두 우호적일 때 비중을 공격적으로 높입니다.
    * **하단 방어:** 시장 상황이 악화되어도 장기 우상향을 고려하여 **최소 30%**의 주식 비중을 유지하도록 설계되었습니다.
    
    ### 2. 채권 (Safety/Income Asset)
    * **결정 원리:** 경기가 둔화(선행지수 하락)될 때 주식의 변동성을 상쇄하는 역할을 합니다. 
    * **상관관계:** 주식 비중이 줄어들 때 채권 비중이 자동으로 늘어나 포트폴리오의 전체 위험을 낮춥니다.
    
    ### 3. 금/원자재 (Hedge Asset)
    * **결정 원리:** 공포 지수(VIX)가 상승하거나 지정학적 리스크가 커질 때 비중을 늘립니다. 
    * **역할:** 위기 상황에서 가치가 상승하여 전체 계좌의 '보험' 역할을 수행합니다.
    
    ### 4. 현금 (Liquidity Asset)
    * **결정 원리:** 시장 과열도(RSI)가 과열권(65 이상)에 진입하면 현금을 확보합니다.
    * **역할:** 단기 조정 시 저가 매수를 위한 '총알'을 준비하는 과정입니다.
    
    ---
    *본 모델은 공격적 비중 가산점이 적용되어 상승장에서 더 높은 수익률을 추구합니다.*
    """)

st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
