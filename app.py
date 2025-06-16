import streamlit as st
import pandas as pd
import math

st.title("전기동 실물 기반 LME 헷지 계산기")

with open("sample.xlsx", "rb") as f:
    st.download_button(
        label="📥 샘플 엑셀 양식 다운로드",
        data=f,
        file_name="sample_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

uploaded_file = st.file_uploader("실물 거래 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    lot_size = 25

    # Purchase Reference 기준 (Supplier → Sell)
    purchase_grouped = df[['Purchase\nReference', 'Lot NW']].dropna().groupby('Purchase\nReference').sum()
    purchase_grouped = purchase_grouped.rename(columns={'Lot NW': 'Physical Quantity (MT)'})
    purchase_grouped['Underhedge Lot'] = (purchase_grouped['Physical Quantity (MT)'] // lot_size).astype(int)
    purchase_grouped['Overhedge Lot'] = (purchase_grouped['Physical Quantity (MT)'] / lot_size).apply(math.ceil)
    purchase_grouped['Underhedge Exposure (MT)'] = (
        purchase_grouped['Physical Quantity (MT)'] - (purchase_grouped['Underhedge Lot'] * lot_size)
    ).round(3)
    purchase_grouped['Overhedge Exposure (MT)'] = (
        (purchase_grouped['Overhedge Lot'] * lot_size) - purchase_grouped['Physical Quantity (MT)']
    ).round(3)
    purchase_grouped.reset_index(inplace=True)
    purchase_grouped['Position Type'] = 'Sell (Supplier)'

    # Sales Reference 기준 (Customer → Buy)
    sales_grouped = df[['Sales\nReference', 'Lot NW']].dropna().groupby('Sales\nReference').sum()
    sales_grouped = sales_grouped.rename(columns={'Lot NW': 'Physical Quantity (MT)'})
    sales_grouped['Underhedge Lot'] = (sales_grouped['Physical Quantity (MT)'] // lot_size).astype(int)
    sales_grouped['Overhedge Lot'] = (sales_grouped['Physical Quantity (MT)'] / lot_size).apply(math.ceil)
    sales_grouped['Underhedge Exposure (MT)'] = (
        sales_grouped['Physical Quantity (MT)'] - (sales_grouped['Underhedge Lot'] * lot_size)
    ).round(3)
    sales_grouped['Overhedge Exposure (MT)'] = (
        (sales_grouped['Overhedge Lot'] * lot_size) - sales_grouped['Physical Quantity (MT)']
    ).round(3)
    sales_grouped.reset_index(inplace=True)
    sales_grouped['Position Type'] = 'Buy (Customer)'

    # 컬럼 통일
    purchase_grouped = purchase_grouped.rename(columns={'Purchase\nReference': 'Reference'})
    sales_grouped = sales_grouped.rename(columns={'Sales\nReference': 'Reference'})

    # 합치기
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