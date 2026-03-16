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
        벤저민 그레이엄의 <span style='color: #2E8B57; font-weight: bold;'>25:75 전략</span> | 
        초보자를 위한 <span style='color: #FF4B4B; font-weight: bold;'>분기별 정기 리밸런싱</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 및 분기별 평균(3개월) 산출 로직
def get_quarterly_indices():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # VIX 평균 계산
        vix_df = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        vix_avg = vix_df['Close'].mean()
        
        # RSI 평균 계산 (SPY 기준)
        spy_df = yf.download("SPY", start=start_date, end=end_date, progress=False)
        delta = spy_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_series = 100 - (100 / (1 + (gain / loss)))
        rsi_avg = rsi_series.mean()
        
        # 공포 & 탐욕 지수 (3개월 평균 심리 모델링)
        fg_avg = 100 - (vix_avg * 2) + (rsi_avg - 50)
        fg_avg = round(max(0, min(100, fg_avg)))
        
        leading_idx = 100.5   # 경기선행지수 (고정값)
        export_growth = 4.6   # 한국 수출 증가율 (고정값)
        
        return round(vix_avg, 2), round(rsi_avg, 2), leading_idx, export_growth, fg_avg
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix, rsi, leading_idx, export_growth, fg_val = get_quarterly_indices()

# 4. 그레이엄 식 비중 결정 로직 (수정된 핵심 로직)
# 기본 주식 비중 점수제 (25%, 35%, 50%, 65%, 75%)
score = 0
if vix < 16: score += 1      # 시장 안정
if rsi < 45: score += 1      # 저평가 매수 기회
if vix > 22: score -= 1      # 시장 불안
if rsi > 60: score -= 1      # 과열 매도 신호

# 점수에 따른 주식 비중 (Min 25% ~ Max 75%)
if score >= 2: stock_w = 75
elif score == 1: stock_w = 65
elif score == 0: stock_w = 50
elif score == -1: stock_w = 35
else: stock_w = 25

# 나머지 안전자산 비분배 (채권 50%, 금 30%, 현금 20% 비율)
safety_total = 100 - stock_w
bond_w = round(safety_total * 0.5)
gold_w = round(safety_total * 0.3)
cash_w = safety_total - bond_w - gold_w

# 지표 상태 텍스트 설정
vix_sig, vix_col, vix_desc = ("안정", "#2E8B57", "비중 확대") if vix < 16 else (("주의", "#FF4B4B", "방어 강화") if vix > 22 else ("적정", "#FFA500", "보통"))
rsi_sig, rsi_col, rsi_desc = ("저평가", "#2E8B57", "분할 매수") if rsi < 45 else (("과열", "#FF4B4B", "점진 매도") if rsi > 60 else ("중립", "#FFA500", "적정"))
fg_sig, fg_col, fg_desc = ("매수 기회", "#2E8B57", "극도의 공포") if fg_val <= 25 else (("과열 주의", "#FF4B4B", "극도의 탐욕") if fg_val >= 75 else ("심리 안정", "#6C757D", "보통"))

# 5. 분기별 안내 섹션
now = datetime.now()
quarter = (now.month - 1) // 3 + 1
st.info(f"📅 **현재는 {now.year}년 {quarter}분기 전략 구간입니다.** (다음 정기 리밸런싱: {now.year if quarter < 4 else now.year+1}년 {(quarter % 4) * 3 + 1}월 1일)")
st.success("💡 본 시스템은 **벤저민 그레이엄의 25:75 원칙**에 따라 주식 비중을 최소 25%에서 최대 75% 사이로 자동 조절합니다.")

# 6. 자산별 권장 비중 카드
st.subheader(f"🚥 이번 분기 그레이엄 식 권장 비중")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)
asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 통합 분석
st.subheader("🔍 분기별 시장 지표 분석 (3개월 평균)")
m1, m2, m3, m4, m5 = st.columns(5)
def mini_card(col, title, val, sig, color, desc, link, help_text):
    col.markdown(f"""<a href="{link}" target="_blank" style="text-decoration: none;" title="{help_text}"><div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;"><p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p><p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p><p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p><p style="color: #999; font-size: 11px; margin:0;">({desc})</p></div></a>""", unsafe_allow_html=True)

mini_card(m1, "3개월 변동성(VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index", "평균 변동성입니다.")
mini_card(m2, "3개월 과열도(RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI", "평균 과열도입니다.")
mini_card(m3, "공포&탐욕 평균", fg_val, fg_sig, fg_col, fg_desc, "https://edition.cnn.com/markets/fear-and-greed", "평균 심리지수입니다.")
mini_card(m4, "경기선행지수", leading_idx, "확장", "#2E8B57", "주도주 집중", "https://www.google.com/search?q=경기선행지수", "경기 방향성입니다.")
mini_card(m5, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "성장 가속", "https://www.google.com/search?q=수출입동향", "경제 기초체력입니다.")

st.divider()

# 8. 상세 ETF 포트폴리오 (기존 틀 유지)
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
col_st, col_bd, col_gd = st.columns(3)
with col_st:
    st.markdown("#### 📈 주식 (Growth)")
    st.markdown("""**🇰🇷 국내 (50%)**: Tiger 200, Rise 코리아밸류업, PLUS 고배당주\n**🇺🇸 미국 (50%)**: Tiger S&P500, 나스닥 100, AI테마""")
with col_bd:
    st.markdown("#### 🏦 채권 (Safety)")
    st.markdown("""**🇺🇸 미국 (60%)**: 30년국채액티브(H), 10년국채\n**🇰🇷 국내 (40%)**: ACE 국고채10년""")
with col_gd:
    st.markdown("#### 🟡 금/현금 (Hedge)")
    st.markdown("""**금**: ACE KRX금현물 ETF\n**현금**: TIGER CD금리액티브""")

st.divider()

# 9. 자산배분 철학 (그레이엄 관점으로 수정)
st.subheader("💡 현명한 투자자의 자산배분 철학")
with st.expander("🧐 벤저민 그레이엄의 '25:75 원칙'이란? (클릭하여 보기)", expanded=True):
    st.markdown(f"""
    본 시스템은 **벤저민 그레이엄**의 가르침을 수치화하여 사회초년생에게 제안합니다.
    
    ### 1. 가변 비중 전략
    * **주식 Max 75%:** 시장이 비관에 빠져 주가가 저렴할 때 주식 비중을 최대화합니다.
    * **주식 Min 25%:** 시장이 낙관에 취해 주가가 과열될 때 주식을 최소화하고 **안전군(채권/금/현금)을 75%까지** 높입니다.

    ### 2. 보수적 운용
    * 주식을 제외한 자산은 채권 위주로 구성하되, 금과 현금을 섞어 어떤 경제 위기에도 버틸 수 있는 **'방어적 포트폴리오'**를 지향합니다.
    """)

st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
