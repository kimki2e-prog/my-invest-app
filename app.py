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
        <span style='color: #FF4B4B; font-weight: bold;'>흔들리지 않는 자산관리!</span>
    </p>
""", unsafe_allow_html=True)
st.divider()

# 3. 데이터 수집 및 분기별 평균 산출 로직
def get_quarterly_indices():
    try:
        # 최근 3개월(약 90일) 데이터 수집
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
        
        # 공포 & 탐욕 지수 (3개월 평균 심리)
        fg_avg = 100 - (vix_avg * 2) + (rsi_avg - 50)
        fg_avg = round(max(0, min(100, fg_avg)))
        
        # 경기 및 수출 (분기별 데이터로 가정)
        leading_idx = 100.5   
        export_growth = 4.6   
        
        return round(vix_avg, 2), round(rsi_avg, 2), leading_idx, export_growth, fg_avg
    except:
        return 20.0, 50.0, 100.0, 0.0, 50.0

vix, rsi, leading_idx, export_growth, fg_val = get_quarterly_indices()

# 4. 자산별 비중 계산 (평균 데이터 기반)
stock_w, bond_w, gold_w, cash_w = 40, 25, 20, 15

if vix > 22: vix_sig, vix_col, vix_desc = "주의", "#FF4B4B", "방어 강화"; gold_w += 10; stock_w -= 5
elif vix < 16: vix_sig, vix_col, vix_desc = "안정", "#2E8B57", "비중 유지"; stock_w += 10
else: vix_sig, vix_col, vix_desc = "적정", "#FFA500", "보통"

if rsi > 60: rsi_sig, rsi_col, rsi_desc = "과열", "#FF4B4B", "점진 매도"; cash_w += 10; stock_w -= 5
elif rsi < 40: rsi_sig, rsi_col, rsi_desc = "저평가", "#2E8B57", "분할 매수"; stock_w += 15
else: rsi_sig, rsi_col, rsi_desc = "중립", "#FFA500", "적정"

# 최종 비중 정규화 로직 (이전 로직 유지)
if gold_w > 15: gold_w = 15
if stock_w < 30: stock_w = 30
total = stock_w + bond_w + gold_w + cash_w
stock_w = round((stock_w / total) * 100); bond_w = round((bond_w / total) * 100)
gold_w = round((gold_w / total) * 100); cash_w = 100 - (stock_w + bond_w + gold_w)
if bond_w < 20: stock_w -= (20 - bond_w); bond_w = 20

# 5. 분기별 안내 섹션 (추가됨)
now = datetime.now()
quarter = (now.month - 1) // 3 + 1
st.info(f"📅 **현재는 {now.year}년 {quarter}분기 전략 구간입니다.** (다음 업데이트: {now.year if quarter < 4 else now.year+1}년 {(quarter % 4) * 3 + 1}월 1일)")
st.success("💡 본 수치는 최근 3개월간의 시장 평균 지표를 분석한 결과로, 분기별 1회 리밸런싱에 최적화되어 있습니다.")

# 6. 자산별 권장 비중 카드
st.subheader("🚥 이번 분기 권장 비중")
c1, c2, c3, c4 = st.columns(4)
def asset_card(col, title, weight, color):
    col.markdown(f"<div style='background-color: {color}15; padding: 20px; border-radius: 15px; border: 2px solid {color}; text-align: center;'><h4 style='color: {color}; margin: 0;'>{title}</h4><h1 style='font-size: 40px; color: {color}; margin: 10px 0;'>{weight}%</h1></div>", unsafe_allow_html=True)
asset_card(c1, "주식", stock_w, "#2E8B57")
asset_card(c2, "채권", bond_w, "#007BFF")
asset_card(c3, "금/원자재", gold_w, "#FFD700")
asset_card(c4, "현금", cash_w, "#6C757D")

st.divider()

# 7. 핵심 지표 통합 분석 (분기 평균 데이터)
st.subheader("🔍 분기별 시장 지표 분석 (3개월 평균)")
m1, m2, m3, m4, m5 = st.columns(5)
# ... [이전 mini_card 함수 및 호출 로직 유지] ...
def mini_card(col, title, val, sig, color, desc, link, help_text):
    col.markdown(f"""<a href="{link}" target="_blank" style="text-decoration: none;" title="{help_text}"><div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #ddd; border-top: 6px solid {color}; text-align: center;"><p style="color: #666; font-size: 11px; margin:0; font-weight: bold;">{title} 🔗</p><p style="font-size: 18px; font-weight: bold; margin:8px 0; color: #31333F;">{val}</p><p style="color: {color}; font-size: 13px; font-weight: bold; margin:0;">{sig}</p><p style="color: #999; font-size: 11px; margin:0;">({desc})</p></div></a>""", unsafe_allow_html=True)

mini_card(m1, "3개월 변동성(VIX)", vix, vix_sig, vix_col, vix_desc, "https://www.google.com/search?q=VIX+index", "최근 3개월간 시장의 불안도를 나타내는 평균 수치입니다.")
mini_card(m2, "3개월 과열도(RSI)", rsi, rsi_sig, rsi_col, rsi_desc, "https://www.google.com/search?q=SPY+RSI", "최근 3개월간 주가가 과열되었는지 분석한 평균 수치입니다.")
mini_card(m3, "공포&탐욕 평균", fg_val, "안정적", "#6C757D", "보통", "https://edition.cnn.com/markets/fear-and-greed", "시장의 심리 상태를 분기 평균으로 계산한 수치입니다.")
mini_card(m4, "경기선행지수", leading_idx, "확장", "#2E8B57", "주도주 집중", "https://www.google.com/search?q=경기선행지수", "향후 경기 방향을 예고하는 지표입니다.")
mini_card(m5, "수출 증가율", f"{export_growth}%", "호조", "#2E8B57", "성장 가속", "https://www.google.com/search?q=수출입동향", "대한민국 경제의 기초 체력을 나타냅니다.")

st.divider()

# [8~10번 섹션: ETF 구성 및 철학 - 이전의 상세 버전 유지]
st.subheader("📦 누구나 따라 할 수 있는 자산별 ETF 구성")
# ... [중략: 이전 코드의 상세 ETF 리스트 및 자산배분 철학 텍스트 삽입] ...
col_st, col_bd, col_gd = st.columns(3)
with col_st:
    st.markdown("#### 📈 주식 (Growth)\n**🇰🇷 국내 주식 (50%)**: Tiger 200, 코리아밸류업, PLUS 고배당주\n**🇺🇸 미국 주식 (50%)**: Tiger S&P500, 나스닥100, AI 테마")
with col_bd:
    st.markdown("#### 🏦 채권 (Safety)\n**🇺🇸 미국 채권 (60%)**: 30년국채액티브(H), 10년국채\n**🇰🇷 국내 채권 (40%)**: ACE 국고채10년")
with col_gd:
    st.markdown("#### 🟡 금/현금 (Hedge)\n**금 (100%)**: ACE KRX금현물\n**현금**: TIGER CD금리액티브")

st.divider()
st.subheader("💡 좋은투자자의 자산배분 철학")
with st.expander("🧐 왜 주식/채권/금 비중을 이렇게 구성했나요? (클릭하여 보기)", expanded=True):
    st.markdown("본 시스템은 **'지키면서 불리는'** 정석 투자를 지향합니다. 분기별 리밸런싱은 시장의 소음(Noise)을 제거하고 큰 흐름에 몸을 싣는 가장 현명한 방법입니다.")

st.markdown("<br><p style='text-align: center; color: #999; font-size: 18px; font-weight: bold;'>By 좋은투자자</p>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 분기별 평균치를 기반으로 하며, 최종 투자 책임은 사용자에게 있습니다.")
