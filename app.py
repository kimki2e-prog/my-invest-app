import streamlit as st
from PIL import Image
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", layout="wide")

# 2. 상단 브랜드 섹션
st.markdown("<h1 style='text-align: center; color: #2E8B57; margin-bottom: 5px;'>나도 할 수 있다! 자산관리</h1>", unsafe_allow_html=True)
st.markdown("""
    <p style='text-align: center; font-size: 20px; color: #666;'>
        초보자를 위한 <span style='color: #2E8B57; font-weight: bold;'>분기별 정기 리밸런싱</span> 시스템 | 
        <span style='color: #FF4B4B; font-weight: bold;'>절대 잃지 않는 투자전략!</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 (분기 평균 및 실시간 데이터 분리)
def get_market_indices():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # [분기 평균용] VIX 및 RSI
        vix_df = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        vix_avg = vix_df['Close'].mean()
        
        spy_df = yf.download("SPY", start=start_date, end=end_date, progress=False)
        delta = spy_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_series = 100 - (100 / (1 + (gain / loss)))
        rsi_avg = rsi_series.mean()

        # [실시간 반영용] 공포 & 탐욕 지수 (가장 최근 종가 기준)
        vix_now = vix_df['Close'].iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        fg_now = 100 - (vix_now * 2) + (rsi_now - 50)
        fg_now = round(max(0, min(100, fg_now)))
        
        leading_idx = 100.5   # 경기선행지수
        export_growth = 4.6   # 한국 수출 증가율
        
        return round(vix_avg, 2), round(rsi_avg, 2), leading_idx, export_growth, fg_now
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix_avg, rsi_avg, leading_idx, export_growth, fg_val = get_market_indices()

# 4. 자산별 비중 계산 로직 (기본값 전략 유지)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

# VIX 평균 기반 조정
if vix_avg > 22: vix_sig, vix_col, vix_desc = "주의", "#FF4B4B", "방어 강화"; gold_w += 10; stock_w -= 5
elif vix_avg < 16: vix_sig, vix_col, vix_desc = "안정", "#2E8B57", "비중 유지"; stock_w += 10
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "보통"

# RSI 평균 기반 조정
if rsi_avg > 60: rsi_sig, rsi_col, rsi_desc = "과열", "#FF4B4B", "점진 매도"; cash_w += 10; stock_w -= 5
elif rsi_avg < 40: rsi_sig, rsi_col, rsi_desc = "저평가", "#2E8B57", "분할 매수"; stock_w += 15
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "적정"

# 실시간 공포 & 탐욕 상태 판별
if fg_val >= 75: fg_sig, fg_col, fg_desc = "극도의 탐욕", "#FF4B4B", "과열 주의"
elif fg_val <= 25: fg_sig, fg_col, fg_desc = "극도의 공포", "#2E8B57", "매수 기회"
elif fg_val >= 55: fg_sig, fg_col, fg_desc = "탐욕", "#FFA500", "추격 금지"
elif fg_val <= 45: fg_sig, fg_col, fg_desc = "공포", "#3CB371", "분할 매수"
else: fg_sig, fg_col, fg_desc = "중립", "#6C757D", "관찰"

# 비중 정규화 로직 (유지)
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100); bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100); cash_w = 100 - (stock_w + bond_w + gold_w)
if bond_w < 20: stock_w -= (20 - bond_w); bond_w = 20

# 5. [추가] 나의 투자 원금 입력 및 금액 산출
st.sidebar.header("💰 나의 투자 금액 계산기")
input_money = st.sidebar.number_input("총 투자 원금을 입력하세요 (단위: 만원)", min_value=0, value=1000, step=10)
st.sidebar.divider()
st.sidebar.subheader("📍 자산별 매수 금액")
st.sidebar.markdown(f"📈 주식: **{round(input_money * stock_w / 100)}** 만원")
st.sidebar.markdown(f"🏦 채권: **{round(input_money * bond_w / 100)}** 만원")
st.sidebar.markdown(f"🟡 금/원자재: **{round(input_money * gold_w / 100)}** 만원")
st.sidebar.markdown(f"💵 현금: **{round(input_money * cash_w / 100)}** 만원")
st.sidebar.info("왼쪽 하단의 상세 ETF 종목 리스트를 참고하여 위 금액만큼 매수하세요!")

# 6. 분기별 안내 섹션
now = datetime.now()
quarter = (now.month - 1) // 3 + 1
st.info(f"📅 **현재는 {now.year}년 {quarter}분기 전략 구간입니다.** (다음 정기 리밸런싱: {now.year if quarter < 4 else now.year+1}년 {(quarter % 4) * 3 + 1}월 1일)")
st.success(f"💡 현재 **{input_money}만원** 기준, 최적의 배분 금액을 산출했습니다. 자산 비중은 3개월 평균 지표를 따르며, 공포&탐욕 지수는 실시간 심리를 반영합니다.")

# 7. 자산별 권장 비중 카드
st.subheader("🚥 이번 분기 권장 비중")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color, amount):
    col.markdown(f"""
        <div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'>
            <h4 style='color: {color}; margin: 0;'>{title}</h4>
            <h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1>
            <p style='color: #333; font-weight: bold; margin: 0;'>매수금액: {amount}만원</p>
        </div>
    """, unsafe_allow_html=True)

asset_card(c1, "주식", stock_w, "#2E8B57", round(input_money * stock_w / 100))
asset_card(c2, "채권", bond_w, "#007BFF", round(input_money * bond_w / 100))
asset_card(c3, "금/원자재", gold_w, "#FFD700", round(input_money * gold_w / 100))
asset_card(c4, "현금", cash_w, "#6C757D", round(input_money * cash_w / 100))

st.divider()

# 8. 핵심 지표 통합 분석
st.subheader("🔍 핵심 지표 통합 분석")
m1, m2, m3, m4, m5 = st.columns(5)
def mini_card(col, title, val, sig, color, desc, link, help_text):
    col.markdown(f"""<a href="{link}" target="_blank" style="text-decoration: none;" title="{help_text}"><div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;"><p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p><p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p><p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p><p style="color: #999; font-size: 11px; margin:0;">({desc})</p></div></a>""", unsafe_allow_html=True)

mini_card(m1, "3개월 변동성(VIX)", vix_avg, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index", "리밸런싱 비중의 기준이 되는 3개월 평균 변동성입니다.")
mini_card(m2, "3개월 과열도(RSI)", rsi_avg, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI", "리밸런싱 비중의 기준이 되는 3개월 평균 과열도입니다.")
mini_card(m3, "공포&탐욕(실시간)", fg_val, fg_sig, fg_col, fg_desc, "https://edition.cnn.com/markets/fear-and-greed", "현재 시점의 시장 심리를 실시간으로 나타냅니다.")
mini_card(m4, "경기선행지수", leading_idx, "확장", "#2E8B57", "주도주 집중", "https://www.google.com/search?q=경기선행지수", "향후 경기 방향을 예고하는 지표입니다.")
mini_card(m5, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "성장 가속", "https://www.google.com/search?q=수출입동향", "대한민국 경제의 기초 체력을 나타냅니다.")

st.divider()

# 9. 상세 ETF 포트폴리오 (무삭제 상세 버전)
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
st.info("💡 아래 비중은 각 자산군(주식, 채권 등) 내에서의 개별 종목 배분 비율입니다.")
col_st, col_bd, col_gd = st.columns(3)

with col_st:
    st.markdown("#### 📈 주식 (Growth)")
    st.markdown("""
    **🇰🇷 국내 주식 (50%)**
    * Tiger 200 (20%) - 대표지수
    * Rise 코리아밸류업 (15%) - 정책수혜
    * PLUS 고배당주 (15%) - 안정성
    
    **🇺🇸 미국 주식 (50%)**
    * Tiger S&P500 (20%) - 핵심지수
    * Rise 미국나스닥 100 (10%) - 성장성
    * Time글로벌 AI인공지능액티브 (10%) - 테마
    * Kodex 미국AI전력핵심인프라 (10%) - 테마
    """)

with col_bd:
    st.markdown("#### 🏦 채권 (Safety)")
    st.markdown("""
    **🇺🇸 미국 채권 (60%)**
    * Kodex 미국30년국채액티브(H) (30%)
    * ACE 미국국채10년액티브(H) (30%)
    
    **🇰🇷 국내 채권 (40%)**
    * ACE 국고채10년 (40%)
    """)

with col_gd:
    st.markdown("#### 🟡 금/원자재 (Hedge)")
    st.markdown("""
    **설정 종목 (100%)**
    * ACE KRX금현물 ETF (100%)
    """)
    st.markdown("#### 💵 현금 (Liquidity)")
    st.markdown("""
    * TIGER CD금리액티브
    * KODEX KOFR금리
    """)

st.divider()

# 10. 자산관리 구성의 논리 (무삭제 상세 버전)
st.subheader("💡 좋은투자자의 자산배분 철학")
with st.expander("🧐 왜 주식/채권/금 비중을 이렇게 구성했나요? (클릭하여 보기)", expanded=True):
    st.markdown("""
    본 시스템은 **'지키면서 불리는'** 자산배분의 정석을 따릅니다.
    
    ### 1. 주식 (Growth): "성장의 엔진"
    * **국내/미국 5:5 배분:** 한국의 저평가 매력(밸류업)과 미국의 압도적 성장성(AI/인프라)을 동시에 잡습니다.
    * **최소 30% 유지:** 시장이 하락해도 주식은 장기 우상향하므로, 반등 시 기회를 놓치지 않기 위한 최소한의 발을 담가둡니다.

    ### 2. 채권 (Safety): "최후의 방어선"
    * **최소 20% 보장:** 금융 위기나 금리 인하기에 주식의 하락을 방어해 주는 가장 강력한 도구입니다. 
    * **미국/한국 혼합:** 달러 기반의 안전자산(미국채)과 국내 금리 상황에 대응하는 국고채를 6:4로 섞어 안정성을 극대화했습니다.

    ### 3. 금 (Hedge): "위기에 강한 보험"
    * **최대 15% 상한:** 금은 위기에는 빛나지만 평소에는 배당이 없습니다. 따라서 전체 수익률을 깎아먹지 않도록 적절한 보험료(15%)만큼만 가입하는 전략입니다.
    * **KRX 금현물:** 선물 비용이 없는 현물 기반 ETF로 장기 보유에 가장 유리합니다.

    ---
    **본 시스템은 분기별 평균 데이터를 통해 시장의 소음(Noise)을 제거하고 큰 흐름에 몸을 싣는 가장 현명한 리밸런싱을 제안합니다.**
    """)

st.divider()

# 11. 하단 서명
st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 자산 비중은 분기 평균, 심리 지표는 실시간 데이터를 기반으로 합니다. 최종 투자 책임은 사용자에게 있습니다.")
