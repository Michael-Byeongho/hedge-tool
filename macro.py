import requests
import pandas as pd

def get_macro_data():
    indicators = []

    # 1. exchangerate.host 환율
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=KRW,EUR,JPY,CNY")
        fx = res.json()['rates']
        indicators.append(('USD/KRW', f"{fx['KRW']:.2f}", 'N/A'))
        indicators.append(('EUR/USD', f"{1/fx['EUR']:.4f}", 'N/A'))
        indicators.append(('USD/JPY', f"{fx['JPY']:.2f}", 'N/A'))
        indicators.append(('USD/CNY', f"{fx['CNY']:.2f}", 'N/A'))
    except Exception as e:
        indicators += [('USD/KRW', 'N/A', 'N/A'), ('EUR/USD', 'N/A', 'N/A'),
                       ('USD/JPY', 'N/A', 'N/A'), ('USD/CNY', 'N/A', 'N/A')]

    # 2. Twelve Data API (지수류)
    twelve_key = "6738806de23947278a07358b05e17d19"
    td_symbols = {
        "DXY": "DXY",
        "NASDAQ": "^IXIC",
        "S&P 500": "^GSPC",
        "US 10Y Treasury": "^TNX",
    }

    for name, symbol in td_symbols.items():
        try:
            url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={twelve_key}"
            r = requests.get(url).json()
            price = r.get("close") or r.get("price")
            change_pct = r.get("percent_change") or "N/A"
            indicators.append((name, price, float(change_pct) if change_pct != "N/A" else "N/A"))
        except:
            indicators.append((name, "N/A", "N/A"))

    # 3. 수동 링크로 유지 (가격 없음)
    indicators.append(('LME Copper 3M', 'N/A', 'N/A'))
    indicators.append(('WTI', 'N/A', 'N/A'))
    indicators.append(('Brent', 'N/A', 'N/A'))

    return pd.DataFrame(indicators, columns=["Indicator", "Value", "% Change"])