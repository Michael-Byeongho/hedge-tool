import yfinance as yf
import pandas as pd

def get_macro_data():
    tickers = {
        "USD/KRW": "KRW=X",
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "JPY=X",
        "USD/CNY": "CNY=X",
        "DXY": "DX-Y.NYB",
        "WTI": "CL=F",
        "Brent": "BZ=F",
        "NASDAQ": "^IXIC",
        "S&P 500": "^GSPC",
        "US 10Y Treasury": "^TNX"
    }

    data = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="2d")
            if len(df) >= 2:
                current = df['Close'].iloc[-1]
                previous = df['Close'].iloc[-2]
                change = (current - previous) / previous * 100
                data.append((name, round(current, 4), round(change, 2)))
            else:
                data.append((name, "N/A", "N/A"))
        except:
            data.append((name, "N/A", "N/A"))

    # LME Copper 3M remains as N/A
    data.append(("LME Copper 3M", "N/A", "N/A"))

    df = pd.DataFrame(data, columns=["Indicator", "Value", "Change (%)"])
    return df