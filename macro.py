import requests
import pandas as pd

def get_macro_data():
    indicators = []

    # 1. exchangerate.host for FX
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=KRW,EUR,JPY,CNY")
        fx = res.json().get("rates", {})
        indicators.append(('USD/KRW', f"{fx.get('KRW', 'N/A'):.2f}" if 'KRW' in fx else 'N/A', 'N/A'))
        indicators.append(('EUR/USD', f"{1/fx.get('EUR'):.4f}" if 'EUR' in fx and fx['EUR'] != 0 else 'N/A', 'N/A'))
        indicators.append(('USD/JPY', f"{fx.get('JPY', 'N/A'):.2f}" if 'JPY' in fx else 'N/A', 'N/A'))
        indicators.append(('USD/CNY', f"{fx.get('CNY', 'N/A'):.2f}" if 'CNY' in fx else 'N/A', 'N/A'))
    except:
        indicators += [('USD/KRW', 'N/A', 'N/A'), ('EUR/USD', 'N/A', 'N/A'),
                       ('USD/JPY', 'N/A', 'N/A'), ('USD/CNY', 'N/A', 'N/A')]

    # 2. FinancialModelingPrep for indices
    fmp_key = "fbcnNIVtK6pqedX3z9XSGvNHTsEMw5aX"
    fmp_map = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DXY": "DX-Y.NYB"
    }
    for name, symbol in fmp_map.items():
        try:
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={fmp_key}"
            r = requests.get(url).json()[0]
            price = r.get("price", "N/A")
            change_pct = r.get("changesPercentage", "N/A")
            indicators.append((name, round(price, 2) if isinstance(price, (int, float)) else "N/A",
                               round(change_pct, 2) if isinstance(change_pct, (int, float)) else "N/A"))
        except:
            indicators.append((name, "N/A", "N/A"))

    # 3. Alpha Vantage for oil
    av_key = "B7DB2AK4ZL4A2S53"
    oil_map = {
        "WTI": "WTI",
        "Brent": "BRENT"
    }
    for name, symbol in oil_map.items():
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={av_key}"
            r = requests.get(url).json()
            quote = r.get("Global Quote", {})
            price = quote.get("05. price", "N/A")
            change_pct = quote.get("10. change percent", "N/A").replace("%", "") if "10. change percent" in quote else "N/A"
            indicators.append((name, price, float(change_pct) if change_pct != "N/A" else "N/A"))
        except:
            indicators.append((name, "N/A", "N/A"))

    # LME Copper
    indicators.append(('LME Copper 3M', 'N/A', 'N/A'))

    return pd.DataFrame(indicators, columns=["Indicator", "Value", "% Change"])