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

# 3. 자산별 비중 계산 (채권 비중을 낮추고 주식 비중을 높인 초기값)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

# [지표별 비중 가감 로직 - 주식 공격성 대폭 강화]
if vix > 25: vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "위험 관리 모드"; gold_w += 15; stock_w -= 10
elif vix < 15: vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "주식 적극 확대"; gold_w -= 10; stock_w += 25 # 주식 가중치 대폭 상향
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "변동성 보통"; 

if rsi > 65: rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "현금 비중 확보"; cash_w += 15; stock_w -= 5
elif rsi < 35: rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "강력 저가 매수"; cash_w -= 10; stock_w += 25 # 주식 가중치 대폭 상향
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "가격 적정"; 

if leading_idx >= 100: eco_sig, eco_col, eco_desc = "확장", "#2E8B57", "경기 주도주 집중"; stock_w += 25; bond_w -= 15 # 채권 비중 대폭 축소
else: eco_sig, eco_col, eco_desc = "수축", "#FF4B4B", "포트폴리오 방어"; stock_w -= 10; bond_w += 10

if export_growth > 0: exp_sig, exp_col, exp_desc = "호조", "#2E8B57", "성장 가속화 전략"; stock_w += 20; gold_w -= 10
else: exp_sig, exp_col, exp_desc = "부진", "#FF4B4B", "보수적 운용"; stock_w -= 15; cash_w += 10

# [비중 제약 및 정규화 로직]
# 1단계: 금 비중 상한 15% 강제 적용
if gold_w > 15:
    gold_w = 15

# 2단계: 주식 최소 30% 보장 및 전체 정규화
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)

if stock_w < 30:
    stock_w = 30

# 3단계: 최종 비중 배분 (채권을 후순위로 밀어 비중 낮춤)
remaining = 100 - stock_w - gold_w
sub_total = bond_w + cash_w
bond_w = round((bond_w / sub_total) * remaining)
cash_w = 100 - stock_w - gold_w - bond_w

# 4. 오늘의 투자 날씨
if stock_w >= 70: weather, w_icon, w_col = "공격적 확장", "🚀", "#2E8B57" # 주식 비중 70% 이상 시 로켓 아이콘
elif stock_w >= 50: weather, w_icon, w_col = "안정적 수익", "☀️", "#3CB371"
elif stock_w >= 30: weather, w_icon, w_col = "보수적 대응", "☁️", "#FFA500"
else: weather, w_icon, w_col = "리스크 관리", "⛈️", "#FF4B4B"

# 5. UI - 상단 기상도
st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 25px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p><h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드 (제목 수정됨)
st.subheader("🚥 자산별 권장 비중")
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
    본 앱의 알고리즘은 **공격적인 주식 비중**을 유지하며 시장 기회에 기민하게 반응합니다.
    
    ### 1. 주식 (Growth Asset) - [최소 30% / 공격적 확장]
    기업 이익(수출)과 경기 지표가 우호적일 때 비중을 최대치로 높입니다. 채권 비중을 희생하더라도 주식 수익률을 우선시하는 공격적 세팅이 적용되었습니다.
    
    ### 2. 채권 (Safety Asset) - [보완적 역할]
    주식 비중이 매우 높을 때는 최소한의 안전 장치 역할만 수행합니다. 경기가 급격히 꺾일 때에만 비중을 늘려 방어합니다.
    
    ### 3. 금/원자재 (Hedge Asset) - [최대 15%]
    포트폴리오의 효율성을 위해 비중을 15% 이하로 제어하면서도, 시장 공포가 커질 때 보험 역할을 충실히 수행하도록 설계되었습니다.
    
    ### 4. 현금 (Liquidity Asset)
    과열 시 수익 실현을 통해 확보하며, 조정 시 주식을 더 담기 위한 유동성 자산입니다.
    
    ---
    *본 모델은 상승장에서의 성과를 극대화하기 위해 설계된 '주식 친화적' 자산 배분 모델입니다.*
    """)

st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
