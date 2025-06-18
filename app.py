import streamlit as st
import pandas as pd
import requests
import math
from macro import get_macro_data

st.set_page_config(page_title="Hedge App", layout="wide")
st.title("📈 실물/선물 포지션 & 매크로 지표 모니터링")

macro_df = get_macro_data()
st.subheader("📊 매크로 지표 (카드형)")

link_map = {
    'USD/KRW': 'https://finance.yahoo.com/quote/KRW=X',
    'EUR/USD': 'https://finance.yahoo.com/quote/EURUSD=X',
    'USD/JPY': 'https://finance.yahoo.com/quote/JPY=X',
    'USD/CNY': 'https://finance.yahoo.com/quote/CNY=X',
    'DXY': 'https://finance.yahoo.com/quote/DX-Y.NYB',
    'WTI': 'https://finance.yahoo.com/quote/CL=F',
    'Brent': 'https://finance.yahoo.com/quote/BZ=F',
    'NASDAQ': 'https://finance.yahoo.com/quote/%5EIXIC',
    'S&P 500': 'https://finance.yahoo.com/quote/%5EGSPC',
    'US 10Y Treasury': 'https://finance.yahoo.com/quote/%5ETNX',
    'LME Copper 3M': 'https://www.investing.com/commodities/copper'
}

cols = st.columns(4)
for idx, row in enumerate(macro_df.itertuples()):
    indicator = row.Indicator
    value = row.Value
    change = row._3

    if isinstance(change, float):
        icon = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
        color = "red" if change > 0 else "blue" if change < 0 else "gray"
        change_str = f"<span style='color:{color};'>{icon} {change:.2f}%</span>"
    else:
        change_str = "<span style='color:gray;'>N/A</span>"

    link = link_map.get(indicator, "#")
    with cols[idx % 4]:
        st.markdown(f'''
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="border:1px solid #ddd;padding:10px;border-radius:10px;
                        background-color:#f9f9f9;width: 80%; margin: auto; font-size:85%;">
                <div style='font-weight:bold;margin-bottom:5px;'>{indicator}</div>
                <div style='font-size:20px;'>{value}</div>
                <div style='font-size:14px;'>변화율: {change_str}</div>
            </div>
        </a>
        ''', unsafe_allow_html=True)

st.markdown("---")
st.header("📦 실물 거래 파일 업로드 및 헷지 분석")

uploaded_file = st.file_uploader("실물 거래 데이터를 업로드하세요 (xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    lot_size = 25

    st.subheader("🔹 공급선 기준 (Sell 포지션)")
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
    st.dataframe(purchase_grouped)

    st.subheader("🔸 판매선 기준 (Buy 포지션)")
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
    st.dataframe(sales_grouped)