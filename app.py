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

# 3. 자산별 비중 계산 로직
stock_w, bond_w, gold_w, cash_w = 25, 40, 20, 15
logic_details = []

# [지표 1] 경기선행지수 & 수출 (실물 경기 및 기업 이익 지표)
logic_details.append("### 📈 실물 경기 및 이익 지표")
logic_details.append("> **경기선행지수와 수출**은 주가 상승의 '연료'인 기업 이익을 결정합니다.")
if leading_idx >= 100 and export_growth > 0:
    stock_w += 25; bond_w -= 10
    logic_details.append("💡 **판단:** 경기 확장 및 수출 호조로 기업 이익 증가가 예상됩니다. **[주식 확대 / 채권 축소]**")
elif leading_idx < 100 and export_growth < 0:
    stock_w -= 15; bond_w += 15; cash_w += 5
    logic_details.append("💡 **판단:** 경기 위축 우려로 안전자산 선호가 강해집니다. **[주식 축소 / 채권·현금 확대]**")
else:
    logic_details.append("💡 **판단:** 지표가 혼조세입니다. 기존 비중을 유지하며 관망합니다.")

# [지표 2] 변동성 VIX (시장 공포 및 리스크 지표)
logic_details.append("### 🚨 시장 공포 지수 (VIX)")
logic_details.append("> **VIX**는 투자자들의 불안감을 나타냅니다. 높을수록 금과 같은 '피난처' 자산이 중요해집니다.")
if vix > 25:
    gold_w += 10; stock_w -= 10
    logic_details.append(f"💡 **판단:** VIX({vix})가 높아 시장이 불안합니다. 위기 방어용 금 비중을 늘립니다. **[금 확대 / 주식 축소]**")
elif vix < 15:
    gold_w -= 5; stock_w += 5
    logic_details.append(f"💡 **판단:** 시장이 매우 안정적입니다. 방어 비용(금)을 줄여 수익률을 높입니다. **[주식 확대 / 금 축소]**")
else:
    logic_details.append(f"💡 **판단:** 시장 변동성이 평이한 수준입니다. 중립을 유지합니다.")

# [지표 3] 과열도 RSI (가격 부담 및 심리 지표)
logic_details.append("### 🌡️ 시장 과열도 (RSI)")
logic_details.append("> **RSI**는 단기적으로 주가가 너무 올랐는지(과열) 내렸는지(침체)를 알려줍니다.")
if rsi > 65:
    cash_w += 10; stock_w -= 10
    logic_details.append(f"💡 **판단:** RSI({rsi}) 기준 시장이 과열되었습니다. '총알(현금)'을 챙겨 조정을 대비합니다. **[현금 확대 / 주식 축소]**")
elif rsi < 35:
    cash_w -= 5; stock_w += 10
    logic_details.append(f"💡 **판단:** 과도한 하락 구간입니다. 챙겨둔 현금으로 저가 매수에 나섭니다. **[주식 확대 / 현금 사용]**")
else:
    logic_details.append(f"💡 **판단:** 가격 부담이 적정한 수준입니다.")

# 비중 정규화 (100% 합계 유지)
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100)
bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100)
cash_w = 100 - (stock_w + bond_w + gold_w)

# 4. 종합 날씨 결정
if stock_w >= 50: weather, w_icon, w_col = "적극적 자산 확장", "☀️", "#2E8B57"
elif stock_w >= 30: weather, w_icon, w_col = "안정적 중립 유지", "🌤️", "#3CB371"
else: weather, w_icon, w_col = "보수적 리스크 방어", "⛈️", "#FF4B4B"

# 5. UI - 상단 날씨
st.markdown(f"""
    <div style='text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 20px; border: 1px solid #eee; margin-bottom: 20px;'>
        <p style='font-size: 16px; color: #666; margin-bottom: 0;'>중기 포트폴리오 기상도</p>
        <h1 style='font-size: 45px; color: {w_col}; margin: 0;'>{w_icon} {weather}</h1>
    </div>
""", unsafe_allow_html=True)

# 6. 자산별 권장 비중 카드
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

asset_card(col1, "주식", stock_w, "#2E8B57", "성장 자산 (국내/해외)")
asset_card(col2, "채권", bond_w, "#007BFF", "수익률 방어 (국채)")
asset_card(col3, "금/원자재", gold_w, "#FFD700", "위험 헤지 (실물)")
asset_card(col4, "현금", cash_w, "#6C757D", "유동성 (CMA/파킹)")

st.divider()

# 7. 시장 지표 인터랙티브 카드
st.subheader("🔍 주요 시장 지표 (클릭 시 상세 정보 🔗)")
st.markdown("""<style>.indicator-card { background-color: #ffffff; padding: 12px; border-radius: 10px; border: 1px solid #ddd; text-align: center; transition: all 0.2s; cursor: pointer; text-decoration: none !important; display: block; } .indicator-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-color: #007bff; }</style>""", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
def link_card(col, title, val, color, url):
    col.markdown(f"""<a href="{url}" target="_blank" class="indicator-card" style="border-top: 5px solid {color};"><div style="font-size: 11px; color: #777;">{title} 🔗</div><div style="font-size: 18px; font-weight: bold; color: #333;">{val}</div></a>""", unsafe_allow_html=True)

link_card(m1, "변동성 VIX", vix, "#2E8B57" if vix<22 else "#FF4B4B", "https://www.google.com/search?q=VIX+index")
link_card(m2, "과열도 RSI", rsi, "#2E8B57" if rsi<40 else "#FF4B4B", "https://www.google.com/search?q=SPY+RSI")
link_card(m3, "경기 선행", leading_idx, "#2E8B57" if leading_idx>=100 else "#FF4B4B", "https://www.google.com/search?q=경기선행지수")
link_card(m4, "한국 수출", f"{export_growth}%", "#2E8B57" if export_growth>0 else "#FF4B4B", "https://www.google.com/search?q=수출입동향")

st.divider()

# 8. 자산배분 근거 (설명 보강됨)
with st.expander("🧐 각 지표가 자산 비중에 미치는 영향 (상세 설명)"):
    st.write(f"본 모델은 **기본 주식 비중 25%**를 기준으로, 아래의 지표 해석을 통해 중기 포트폴리오를 조정합니다.")
    for d in logic_details:
        st.markdown(d)
    st.info("💡 이 전략은 특정 자산의 폭락에 대비하고, 장기적으로 우상향하는 자산에 올라타는 '올웨더 스타일' 변형 전략입니다.")

st.caption("※ 본 데이터는 투자 참고용이며 최종 판단은 투자자 본인에게 있습니다.")
