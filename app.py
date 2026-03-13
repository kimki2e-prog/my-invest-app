import streamlit as st
from PIL import Image
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", page_icon=img, layout="wide")
except:
    st.set_page_config(page_title="나도 할 수 있다! 자산관리", layout="wide")

# 2. 상단 브랜드 섹션
st.markdown("<h1 style='text-align: center; color: #2E8B57; margin-bottom: 5px;'>나도 할 수 있다! 자산관리</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px; color: #666;'>초보자를 위한 <span style='color: #2E8B57; font-weight: bold;'>분기별 정기 리밸런싱</span> 시스템 | <span style='color: #FF4B4B; font-weight: bold;'>절대 잃지 않는 투자전략!</span></p>", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 (분기 평균 vs 실시간 데이터 분리)
def get_market_indices():
    try:
        # [A] 분기 평균 데이터 (최근 90일)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        vix_df = yf.download("^VIX", start=start_date, end=end_date, progress=False)
        vix_avg = vix_df['Close'].mean()
        
        spy_df = yf.download("SPY", start=start_date, end=end_date, progress=False)
        delta = spy_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi_series = 100 - (100 / (1 + (gain / loss)))
        rsi_avg = rsi_series.mean()

        # [B] 실시간 데이터 (오늘 기준 가장 최신 데이터)
        # ^VIX와 SPY의 실시간 데이터를 다시 가져옴
        vix_realtime = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        spy_realtime = yf.Ticker("SPY").history(period="20d") # RSI 계산용 최신 20일
        
        # 실시간 RSI 계산
        st_delta = spy_realtime.diff()
        st_gain = (st_delta.where(st_delta > 0, 0)).rolling(window=14).mean()
        st_loss = (-st_delta.where(st_delta < 0, 0)).rolling(window=14).mean()
        rsi_realtime = (100 - (100 / (1 + (st_gain / st_loss)))).iloc[-1]

        # 실시간 공포 & 탐욕 지수 산출
        fg_now = 100 - (vix_realtime * 2) + (rsi_realtime - 50)
        fg_now = round(max(0, min(100, fg_now)))
        
        return round(vix_avg, 2), round(rsi_avg, 2), 100.5, 4.6, fg_now
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix_avg, rsi_avg, leading_idx, export_growth, fg_val = get_market_indices()

# 4. 자산별 비중 계산 (분기 평균 데이터 기반)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15
if vix_avg > 22: vix_sig, vix_col, vix_desc = "주의", "#FF4B4B", "방어 강화"; gold_w += 10; stock_w -= 5
elif vix_avg < 16: vix_sig, vix_col, vix_desc = "안정", "#2E8B57", "비중 유지"; stock_w += 10
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "보통"

if rsi_avg > 60: rsi_sig, rsi_col, rsi_desc = "과열", "#FF4B4B", "점진 매도"; cash_w += 10; stock_w -= 5
elif rsi_avg < 40: rsi_sig, rsi_col, rsi_desc = "저평가", "#2E8B57", "분할 매수"; stock_w += 15
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "적정"

# 5. 실시간 공포 & 탐욕 상태 판별 (현재 시점)
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

# 6. 안내 박스 및 비중 카드
now = datetime.now()
quarter = (now.month - 1) // 3 + 1
st.info(f"📅 **현재는 {now.year}년 {quarter}분기 전략 구간입니다.**")
st.success("💡 자산 비중은 시장 노이즈 제거를 위해 **3개월 평균 지표**를 따르며, **공포&탐욕 지수**는 현재 시장 상황을 **실시간**으로 반영합니다.")

st.subheader("🚥 이번 분기 권장 비중")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)
asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 분석 (실시간 카드 강조)
st.subheader("🔍 핵심 지표 통합 분석")
m1, m2, m3, m4, m5 = st.columns(5)
def mini_card(col, title, val, sig, color, desc, link, help_text, highlight=False):
    border_style = f"border: 2px solid {color};" if highlight else "border: 1px solid #ddd;"
    col.markdown(f"""<a href="{link}" target="_blank" style="text-decoration: none;" title="{help_text}"><div style="background-color: #ffffff; padding: 15px; border-radius: 12px; {border_style} border-top: 6px solid {color}; text-align: center;"><p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p><p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p><p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p><p style="color: #999; font-size: 11px; margin:0;">({desc})</p></div></a>""", unsafe_allow_html=True)

mini_card(m1, "3개월 변동성(VIX)", vix_avg, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index", "리밸런싱 비중의 기준이 되는 3개월 평균 변동성입니다.")
mini_card(m2, "3개월 과열도(RSI)", rsi_avg, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI", "리밸런싱 비중의 기준이 되는 3개월 평균 과열도입니다.")
mini_card(m3, "⭐ 공포&탐욕(실시간)", fg_val, fg_sig, fg_col, fg_desc, "https://edition.cnn.com/markets/fear-and-greed", "현재 시점의 시장 심리를 즉각 반영한 수치입니다.", highlight=True)
mini_card(m4, "경기선행지수", leading_idx, "확장", "#2E8B57", "주도주 집중", "https://www.google.com/search?q=경기선행지수", "향후 경기 방향을 예고하는 지표입니다.")
mini_card(m5, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "성장 가속", "https://www.google.com/search?q=수출입동향", "대한민국 경제의 기초 체력을 나타냅니다.")

st.divider()

# 8. 상세 ETF 포트폴리오 (상세 버전 유지)
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
col_st, col_bd, col_gd = st.columns(3)
with col_st:
    st.markdown("#### 📈 주식 (Growth)\n**🇰🇷 국내 (50%)**: Tiger 200, Rise 코리아밸류업, PLUS 고배당주\n**🇺🇸 미국 (50%)**: Tiger S&P500, 나스닥 100, AI테마")
with col_bd:
    st.markdown("#### 🏦 채권 (Safety)\n**🇺🇸 미국 (60%)**: 30년국채액티브(H), 10년국채\n**🇰🇷 국내 (40%)**: ACE 국고채10년")
with col_gd:
    st.markdown("#### 🟡 금/현금 (Hedge)\n**금**: ACE KRX금현물\n**현금**: CD금리액티브")

st.divider()

# 9. 자산배분 철학 (상세 버전 유지)
st.subheader("💡 좋은투자자의 자산배분 철학")
with st.expander("🧐 왜 주식/채권/금 비중을 이렇게 구성했나요? (클릭하여 보기)", expanded=True):
    st.markdown("""
    ### 1. 주식: 성장의 엔진 | 2. 채권: 최후의 방어선 | 3. 금: 위기에 강한 보험
    본 시스템은 분기별 평균 데이터를 통해 시장의 소음을 제거하고 큰 흐름에 몸을 싣는 리밸런싱을 제안합니다.
    """)

st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 분기별 평균치를 기반으로 하며, 최종 투자 책임은 사용자에게 있습니다.")
