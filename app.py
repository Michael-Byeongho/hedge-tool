import streamlit as st
import pandas as pd
import math
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

st.title("전기동 실물 기반 LME 헷지 계산기 + 매크로 인덱스")

# 1. 📥 샘플 엑셀 다운로드
with open("sample.xlsx", "rb") as f:
    st.download_button(
        label="📥 샘플 엑셀 양식 다운로드",
        data=f,
        file_name="sample_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 2. 📊 매크로 인덱스 수집
st.subheader("📈 주요 매크로 지표")

tickers = {
    'USD/KRW': 'KRW=X',
    'EUR/USD': 'EURUSD=X',
    'USD/JPY': 'JPY=X',
    'USD/CNY': 'CNY=X',
    'DXY': 'DX-Y.NYB',
    'WTI': 'CL=F',
    'Brent': 'BZ=F',
    'NASDAQ': '^IXIC',
    'S&P 500': '^GSPC',
    'US 10Y Treasury': '^TNX'
}

today = datetime.now()
yesterday = today - timedelta(days=1)
macro_data = []

for name, symbol in tickers.items():
    try:
        data = yf.download(symbol, start=yesterday.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))
        if not data.empty:
            latest_close = float(data['Close'].iloc[-1])
            prev_close = float(data['Close'].iloc[0])
            pct_change = ((latest_close - prev_close) / prev_close) * 100
            macro_data.append({
                'Indicator': name,
                'Value': round(latest_close, 4),
                'Change (%)': round(pct_change, 2)
            })
        else:
            macro_data.append({'Indicator': name, 'Value': 'N/A', 'Change (%)': 'N/A'})
    except:
        macro_data.append({'Indicator': name, 'Value': 'Error', 'Change (%)': 'Error'})

# LME Copper 크롤링
try:
    url = "https://www.investing.com/commodities/copper"
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    price_tag = soup.find("span", {"data-test": "instrument-price-last"})
    price = float(price_tag.text.replace(',', '')) if price_tag else 'N/A'
    macro_data.append({'Indicator': 'LME Copper 3M', 'Value': price, 'Change (%)': 'N/A'})
except:
    macro_data.append({'Indicator': 'LME Copper 3M', 'Value': 'Error', 'Change (%)': 'Error'})

macro_df = pd.DataFrame(macro_data)
