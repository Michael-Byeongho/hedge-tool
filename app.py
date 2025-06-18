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
st.dataframe(macro_df)

# 3. 📂 파일 업로드 및 실물 포지션 계산
uploaded_file = st.file_uploader("실물 거래 엑셀 파일을 업로드하세요", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    lot_size = 25

    # Purchase Reference
    purchase_grouped = df[['Purchase\nReference', 'Lot NW']].dropna().groupby('Purchase\nReference').sum()
    purchase_grouped = purchase_grouped.rename(columns={'Lot NW': 'Physical Quantity (MT)'})
    purchase_grouped['Underhedge Lot'] = (purchase_grouped['Physical Quantity (MT)'] // lot_size).astype(int)
    purchase_grouped['Overhedge Lot'] = (purchase_grouped['Physical Quantity (MT)'] / lot_size).apply(math.ceil)
    purchase_grouped['Underhedge Exposure (MT)'] = (
        purchase_grouped['Physical Quantity (MT)'] - (purchase_grouped['Underhedge Lot'] * lot_size)).round(3)
    purchase_grouped['Overhedge Exposure (MT)'] = (
        (purchase_grouped['Overhedge Lot'] * lot_size) - purchase_grouped['Physical Quantity (MT)']).round(3)
    purchase_grouped.reset_index(inplace=True)
    purchase_grouped['Position Type'] = 'Sell (Supplier)'

    # Sales Reference
    sales_grouped = df[['Sales\nReference', 'Lot NW']].dropna().groupby('Sales\nReference').sum()
    sales_grouped = sales_grouped.rename(columns={'Lot NW': 'Physical Quantity (MT)'})
    sales_grouped['Underhedge Lot'] = (sales_grouped['Physical Quantity (MT)'] // lot_size).astype(int)
    sales_grouped['Overhedge Lot'] = (sales_grouped['Physical Quantity (MT)'] / lot_size).apply(math.ceil)
    sales_grouped['Underhedge Exposure (MT)'] = (
        sales_grouped['Physical Quantity (MT)'] - (sales_grouped['Underhedge Lot'] * lot_size)).round(3)
    sales_grouped['Overhedge Exposure (MT)'] = (
        (sales_grouped['Overhedge Lot'] * lot_size) - sales_grouped['Physical Quantity (MT)']).round(3)
    sales_grouped.reset_index(inplace=True)
    sales_grouped['Position Type'] = 'Buy (Customer)'

    # 합치기
    purchase_grouped = purchase_grouped.rename(columns={'Purchase\nReference': 'Reference'})
    sales_grouped = sales_grouped.rename(columns={'Sales\nReference': 'Reference'})
    result = pd.concat([purchase_grouped, sales_grouped], ignore_index=True)

    st.subheader("📊 Reference별 헷지 요약")
    st.dataframe(result)

    st.markdown("""
    ### 📌 해석 가이드
    - **Sell (Supplier)**: 선물 매도 기반 숏 포지션
      - Underhedge → 상승 시 리스크 줄임 (보수적)
      - Overhedge → 하락 시 수익성 확보 (공격적)
    - **Buy (Customer)**: 선물 매수 기반 롱 포지션
      - Underhedge → 상승 시 수익성 확보 (공격적)
      - Overhedge → 하락 시 리스크 줄임 (보수적)
    """)
