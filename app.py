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

# 3. 자산별 비중 계산 (기본 설정)
stock_w, bond_w, gold_w, cash_w = 25, 40, 20, 15

# [지표별 비중 가감 로직]
if vix > 25: vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "금 비중 상한까지 확보"; gold_w += 15; stock_w -= 15
elif vix < 15: vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "주식 적극 확대"; gold_w -= 10; stock_w += 15
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "변동성 보통"; 

if rsi > 65: rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "현금 비중 확보"; cash_w += 10; stock_w -= 10
elif rsi < 35: rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "적극 저가 매수"; cash_w -= 10; stock_w += 20
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "가격 적정"; 

if leading_idx >= 100: eco_sig, eco_col, eco_desc = "확장", "#2E8B57", "경기 주도주 확대"; stock_w += 20; bond_w -= 10
else: eco_sig, eco_col, eco_desc = "수축", "#FF4B4B", "방어 자산 확대"; stock_w -= 10; bond_w += 15

if export_growth > 0: exp_sig, exp_col, exp_desc = "호조", "#2E8B57", "수익 극대화 전략"; stock_w += 15; gold_w -= 5
else: exp_sig, exp_col, exp_desc = "부진", "#FF4B4B", "보수적 대응"; stock_w -= 15; cash_w += 10

# [중요] 비중 제약 조건 적용 (금 상한 15% / 주식 하한 30%)
# 1단계: 금 비중 제한
if gold_w > 15:
    gold_excess = gold_w - 15
    gold_w = 15
    bond_w += gold_excess # 넘치는 금 비중은 채권으로 이동

# 2단계: 주식 비중 제한 및 정규화
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)

if stock_w < 30:
    stock_diff = 30 - stock_w
    stock_w = 30
    bond_w -= stock_diff # 부족한 주식 비중은 채권에서 차감

# 3단계: 최종 정규화 (100% 합계 보정)
remaining_w = 100 - stock_w
sub_total = bond_w + gold_w + cash_w
bond_w = round((bond_w / sub_total) * remaining_w)
gold_w = round((gold_w / sub_total) * remaining_w)
cash_w = 100 - (stock_w + bond_w + gold_w)

# 다시 한번 금 상한 강제 보정 (정규화 과정에서 소폭 넘을 수 있음)
if gold_w > 15:
    g_diff = gold_w - 15
    gold_w = 15
    bond_w += g_diff

# 4. 오늘의 투자 날씨
if stock_w >= 65: weather, w_icon, w_col = "적극적 공격", "🔥", "#2E8B57"
elif stock_w >= 45: weather, w_icon, w_col = "안정적 확장", "☀️", "#3CB371"
elif stock_w >= 30: weather, w_icon, w_col = "보수적 방어", "☁️", "#FFA500"
else: weather, w_icon, w_col = "위기 관리", "⛈️", "#FF4B4B"

# 5. UI - 상단 기상도
st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 25px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p><h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
st.subheader("🚥 자산별 권장 비중 (금 15% 상한 적용)")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 통합 분석
st.subheader("🔍 핵심 지표 통합 분석 (데이터 + 시그널 🔗)")
m1, m2, m3, m4 = st.columns(4)
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

mini_card(m1, "공포 지수 (VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
mini_card(m2, "과열도 (RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")
mini_card(m3, "경기 선행 (지수)", leading_idx, eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수")
mini_card(m4, "한국 수출 (증가율)", f"{export_growth}%", exp_sig, exp_col, exp_desc, "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 자산배분 전략 상세 가이드
st.subheader("📑 자산배분 전략 상세 가이드")
with st.expander("📚 이 포트폴리오는 어떤 원리로 결정되나요? (상세 설명 보기)", expanded=True):
    st.markdown("""
    본 앱은 **주식(최소 30%)**과 **금(최대 15%)**의 비중 범위를 고정한 채, 매크로 지표에 따라 자산을 동적으로 배분합니다.
    
    ### 1. 주식 (Growth Asset) - [최소 30%]
    한국 수출과 경기선행지수를 기반으로 비중을 결정합니다. 시장 우호 시 적극적인 수익을 추구하며, 하락장에서도 30%의 비중은 유지하여 상승 전환을 대비합니다.
    
    ### 2. 채권 (Safety Asset)
    주식과 금의 비중을 제외한 나머지 부분을 채권과 현금이 나누어 가집니다. 경기가 둔화될 때 비중이 자연스럽게 늘어나 변동성을 방어합니다.
    
    ### 3. 금/원자재 (Hedge Asset) - [최대 15%]
    공포 지수(VIX)가 급등할 때 비중을 높여 보험 역할을 수행합니다. 다만, 수익률 효율을 위해 **최대 15%**를 넘지 않도록 설계되었습니다.
    
    ### 4. 현금 (Liquidity Asset)
    RSI 과열 시 비중을 높여 하락장에서의 매수 기회를 준비합니다.
    
    ---
    *본 모델은 리스크 관리(금 상한)와 수익 추구(주식 하한)의 균형을 맞춘 중기 전략입니다.*
    """)

st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
