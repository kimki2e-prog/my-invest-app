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

# 3. 자산별 비중 계산 (기본 주식 25% -> 최소 30% 보정 로직 포함)
stock_w, bond_w, gold_w, cash_w = 25, 40, 20, 15

# [지표별 상태 및 설명 정의]
# 1. 공포 지수 (VIX)
if vix > 25:
    gold_w += 10; stock_w -= 10
    vix_sig, vix_col, vix_desc = "위험", "#FF4B4B", "불안 확산으로 금 비중 확대"
elif vix < 15:
    gold_w -= 5; stock_w += 5
    vix_sig, vix_col, vix_desc = "안전", "#2E8B57", "심리 안정으로 주식 비중 확대"
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "변동성 평이, 중립 유지"

# 2. 과열도 (RSI)
if rsi > 65:
    cash_w += 10; stock_w -= 10
    rsi_sig, rsi_col, rsi_desc = "주의", "#FF4B4B", "단기 과열로 현금 비중 확보"
elif rsi < 35:
    cash_w -= 5; stock_w += 10
    rsi_sig, rsi_col, rsi_desc = "기회", "#2E8B57", "과매도로 주식 저가 매수 시점"
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "가격 부담 적정, 관망 유지"

# 3. 경기 선행 (지수)
if leading_idx >= 100:
    stock_w += 15; bond_w -= 5
    eco_sig, eco_col, eco_desc = "확장", "#2E8B57", "경기 회복기로 주식 비중 확대"
else:
    stock_w -= 10; bond_w += 10
    eco_sig, eco_col, eco_desc = "수축", "#FF4B4B", "경기 둔화로 채권 비중 확대"

# 4. 한국 수출 (증가율)
if export_growth > 0:
    stock_w += 10; gold_w -= 5
    exp_sig, exp_col, exp_desc = "호조", "#2E8B57", "수출 증가로 기업 이익 개선"
else:
    stock_w -= 10; cash_w += 5
    exp_sig, exp_col, exp_desc = "부진", "#FF4B4B", "수출 감소로 보수적 대응"

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
if stock_w >= 60: weather, w_icon, w_col = "공격적 확장", "☀️", "#2E8B57"
elif stock_w >= 40: weather, w_icon, w_col = "안정적 중립", "🌤️", "#3CB371"
else: weather, w_icon, w_col = "보수적 방어", "⛈️", "#FF4B4B"

# 5. UI - 상단 기상도
st.markdown(f"<div style='text-align: center; background-color: #f8f9fa; padding: 25px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 25px;'><p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p><h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1></div>", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
st.subheader("🚥 자산별 권장 비중 (주식 최소 30%)")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 4분할 통합 분석 (이전 버전 복구 및 강화)
st.subheader("🔍 핵심 지표 통합 분석 (데이터 + 설명 + 링크 🔗)")

st.markdown("""<style>.integrated-card { background-color: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e0e0e0; transition: all 0.3s ease; cursor: pointer; text-decoration: none !important; display: block; height: 180px; }.integrated-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); border-color: #007bff; }</style>""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

def unified_card(col, title, val, sig, color, desc, url):
    col.markdown(f"""
        <a href="{url}" target="_blank" class="integrated-card" style="border-top: 6px solid {color};">
            <div style="font-size: 12px; color: #666; font-weight: bold; margin-bottom: 8px;">{title} 🔗</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
                <span style="font-size: 20px; font-weight: 800; color: #222;">{val}</span>
                <span style="font-size: 14px; font-weight: bold; color: {color};">{sig}</span>
            </div>
            <div style="font-size: 13px; color: #555; line-height: 1.4; border-top: 1px solid #eee; padding-top: 8px;">{desc}</div>
        </a>
    """, unsafe_allow_html=True)

unified_card(m1, "공포 지수 (VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index")
unified_card(m2, "과열도 (RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI")
unified_card(m3, "경기 선행 (지수)", leading_idx, eco_sig, eco_col, eco_desc, "https://www.google.com/search?q=경기선행지수")
unified_card(m4, "한국 수출 (증가율)", f"{export_growth}%", exp_sig, exp_col, exp_desc, "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 자산배분 전략 상세 가이드
st.subheader("📑 자산배분 전략 상세 가이드")
with st.expander("📚 각 지표가 자산 비중에 미치는 영향 (상세 설명 보기)", expanded=True):
    st.markdown(f"""
    ### 1. 공포 지수 (VIX)
    투자자의 불안감을 측정합니다. 현재 **{vix_sig}** 상태로, 이에 따라 **{vix_desc}** 전략을 취합니다.
    
    ### 2. 과열도 (RSI)
    가격의 단기적 위치를 나타냅니다. 현재 **{rsi_sig}** 상태이며, **{rsi_desc}**를 통해 리스크를 관리합니다.
    
    ### 3. 경기 선행 (지수)
    향후 3~6개월 뒤의 실물 경기를 예고합니다. 현재 **{eco_sig}** 구간으로 판단되어 **{eco_desc}** 중입니다.
    
    ### 4. 한국 수출 (증가율)
    기업 실적의 핵심 선행 지표입니다. 현재 **{exp_sig}** 상태이며, **{exp_desc}** 로직이 적용되었습니다.
    
    ---
    *주식 최소 비중 30% 원칙에 따라, 어떤 상황에서도 시장 참여를 유지하며 자산 간 리밸런싱을 통해 방어력을 극대화합니다.*
    """)

st.caption("※ 본 데이터는 2026년 기준이며, 투자 판단의 최종 책임은 사용자에게 있습니다.")
