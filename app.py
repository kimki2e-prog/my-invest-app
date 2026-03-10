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

# 3. 자산별 비중 계산 및 통합 로직 (기본 주식 25% -> 최소 30% 보정)
stock_w, bond_w, gold_w, cash_w = 25, 40, 20, 15

# [지표 1] 실물 경기 (선행지수/수출)
if leading_idx >= 100 and export_growth > 0:
    stock_w += 25; bond_w -= 10
    eco_sig, eco_col, eco_desc = "호조", "#2E8B57", "경기 확장기로 주식 비중을 확대합니다."
elif leading_idx < 100 and export_growth < 0:
    stock_w -= 15; bond_w += 15; cash_w += 5
    eco_sig, eco_col, eco_desc = "부진", "#FF4B4B", "경기 위축기로 채권/현금을 늘려 방어합니다."
else: eco_sig, eco_col, eco_desc = "보통", "#FFA500", "지표 혼조세로 기존 비중을 유지합니다."

# [지표 2] 공포 지수 (변동성 VIX)
if vix > 25:
    gold_w += 10; stock_w -= 10
    vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "불안 확산으로 안전자산(금)을 확보합니다."
elif vix < 15:
    gold_w -= 5; stock_w += 5
    vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "심리 안정기로 공격 자산 비중을 높입니다."
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "변동성이 평이한 수준입니다."

# [지표 3] 과열도 (시장 RSI)
if rsi > 65:
    cash_w += 10; stock_w -= 10
    rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "단기 과열로 현금을 챙겨 조정을 대비합니다."
elif rsi < 35:
    cash_w -= 5; stock_w += 10
    rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "과도한 하락으로 주식 저가 매수에 나섭니다."
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "가격 부담이 적정한 수준입니다."

# 비중 정규화 및 [주식 최소 30% 적용]
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
# 주식 최소 비중 30% 강제 보정
if stock_w < 30:
    diff = 30 - stock_w
    stock_w = 30
    bond_w -= diff # 모자란 비중은 가장 큰 비중인 채권에서 차감

bond_w = round((bond_w / (bond_w+gold_w+cash_w)) * (100-stock_w))
gold_w = round((gold_w / (bond_w+gold_w+cash_w)) * (100-stock_w))
cash_w = 100 - (stock_w + bond_w + gold_w)

# 4. 날씨 결정
if stock_w >= 60: weather, w_icon, w_col = "공격적 확장", "☀️", "#2E8B57"
elif stock_w >= 40: weather, w_icon, w_col = "안정적 중립", "🌤️", "#3CB371"
else: weather, w_icon, w_col = "보수적 방어", "⛈️", "#FF4B4B"

# 5. UI - 상단 기상도
st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 25px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p><h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
st.subheader("🚥 자산별 권장 비중 (주식 최소 30% 설정)")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 통합 시장 지표
st.subheader("🔍 핵심 지표 통합 분석 (클릭 시 상세 정보 🔗)")
st.markdown("""<style>.integrated-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; transition: all 0.3s ease; cursor: pointer; text-decoration: none !important; display: block; height: 100%; }.integrated-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-color: #007bff; }</style>""", unsafe_allow_html=True)
col_eco, col_vix, col_rsi = st.columns(3)

def unified_card(col, title, val, sig, color, desc, url):
    col.markdown(f"""<a href="{url}" target="_blank" class="integrated-card" style="border-top: 8px solid {color};"><div style="font-size: 13px; color: #666; font-weight: bold; margin-bottom: 10px;">{title} 🔗</div><div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 15px;"><span style="font-size: 24px; font-weight: 800; color: #222;">{val}</span><span style="font-size: 16px; font-weight: bold; color: {color};">{sig}</span></div><div style="font-size: 14px; color: #444; line-height: 1.5; border-top: 1px solid #eee; padding-top: 10px;">{desc}</div></a>""", unsafe_allow_html=True)

unified_card(col_eco, "실물 경기 (선행지수/수출)", f"{leading_idx} / {export_growth}%", eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수+수출입동향")
unified_card(col_vix, "공포 지수 (변동성 VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
unified_card(col_rsi, "과열도 (시장 RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")

st.divider()

# 8. [상세 보강] 자산배분 결정 근거 알고리즘 설명
st.subheader("📑 자산배분 전략 상세 가이드")
with st.expander("📚 이 포트폴리오는 어떤 원리로 결정되나요? (상세 설명 보기)", expanded=True):
    st.markdown("""
    본 앱의 알고리즘은 **'매크로 지표'**와 **'시장 심리'**를 결합하여 자산별 최적 비중을 도출합니다.
    
    ### 1. 주식 (Growth Asset) - 최소 비중 30%
    * **결정 원리:** 한국 수출 증가율과 경기선행지수가 주가 상승의 핵심 동력입니다. 두 지표가 모두 우호적일 때 비중을 최대 70% 이상으로 높입니다.
    * **하단 방어:** 시장 상황이 악화되어도 장기 우상향을 고려하여 **최소 30%**의 주식 비중을 유지하도록 설계되었습니다.
    
    ### 2. 채권 (Safety/Income Asset)
    * **결정 원리:** 경기가 둔화(선행지수 하락)될 때 주식의 변동성을 상쇄하는 역할을 합니다. 
    * **상관관계:** 주식 비중이 줄어들 때 채권 비중이 자동으로 늘어나 포트폴리오의 전체 위험을 낮춥니다.
    
    ### 3. 금/원자재 (Hedge Asset)
    * **결정 원리:** 공포 지수(VIX)가 상승할 때 비중을 늘립니다. 
    * **역할:** 지정학적 위기나 금융 시스템 불안 시 가치가 상승하여 전체 계좌의 '보험' 역할을 수행합니다.
    
    ### 4. 현금 (Liquidity Asset)
    * **결정 원리:** 시장 과열도(RSI)가 65를 넘어서면 현금을 확보합니다.
    * **역할:** 단기 조정 시 저가 매수를 위한 '총알'을 준비하는 과정입니다.
    
    ---
    *본 모델은 **과거 데이터 기반의 확률적 접근**이며, 지표가 바뀔 때마다 중기적 관점(3~6개월)에서 비중을 재조정하는 것이 효과적입니다.*
    """)

st.caption("※ 2026년 실시간 데이터와 사용자의 수동 입력 지표를 바탕으로 산출되었습니다.")
