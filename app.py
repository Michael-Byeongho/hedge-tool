import streamlit as st
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

    icon = "🔺" if isinstance(change, float) and change > 0 else "🔻" if isinstance(change, float) and change < 0 else "➖"
    color = "red" if icon == "🔺" else "blue" if icon == "🔻" else "gray"
    change_str = f"<span style='color:{color};'>{icon} {change}%</span>" if change != "N/A" else "<span style='color:gray;'>N/A</span>"

    link = link_map.get(indicator, "#")
    with cols[idx % 4]:
        st.markdown(
            f"""
            <a href="{link}" target="_blank" style="text-decoration:none;">
                <div style="border:1px solid #ddd;padding:10px;border-radius:10px;
                            background-color:#f9f9f9;width: 80%; margin: auto; font-size:85%;">
                    <div style='font-weight:bold;margin-bottom:5px;'>{indicator}</div>
                    <div style='font-size:20px;'>{value}</div>
                    <div style='font-size:14px;'>변화율: {change_str}</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )