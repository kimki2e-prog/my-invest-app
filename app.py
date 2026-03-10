import streamlit as st
from PIL import Image
import yfinance as yf

# 1. 페이지 설정
try:
    img = Image.open("logo.png")
    st.set_page_config(page_title="중기 자산배분 전략실", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="중기 자산배분 전략실")

# 2. 데이터 수집 함수
def get_market_indices():
    try:
        # VIX (실시간 심리)
        vix_data = yf.Ticker("^VIX").history(period="1d")
        vix = vix_data['Close'].iloc[-1]
        
        # 공포탐욕 대용 (RSI)
        spy = yf.Ticker("SPY").history(period="20d")
        delta = spy['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # 경기선행지수 순환변동치 (한국 통계청 최근 발표치 반영)
        leading_idx = 100.5 
        
        return round(vix, 2), round(rsi, 2), leading_idx
    except:
        return 20.0, 50.0, 100.0

vix, rsi, leading_idx = get_market_indices()

# 3. 개별 신호등 판별
v_sig, v_col = ("안전", "#2E8B57") if vix < 20 else (("위험", "#FF4B4B") if vix > 30 else ("주의", "#FFA500"))
f_sig, f_col = ("기회", "#2E8B57") if rsi < 35 else (("과열", "#FF4B4B") if rsi > 65 else ("보통", "#FFA500"))
l_sig, l_col = ("확장", "#2E8B57") if leading_idx >= 100 else ("수축", "#FF4B4B")

# 4. 3~6개월
