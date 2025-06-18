import requests
import pandas as pd

def get_macro_data():
    indicators = []

    # 1. exchangerate.host 환율
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=KRW,EUR,JPY,CNY")
        fx = res.json().get("rates", {})
        indicators.append(('USD/KRW', f"{fx.get('KRW', 'N/A'):.2f}" if 'KRW' in fx else 'N/A', 'N/A'))
        indicators.append(('EUR/USD', f"{1/fx.get('EUR'):.4f}" if 'EUR' in fx and fx['EUR'] != 0 else 'N/A', 'N/A'))
        indicators.append(('USD/JPY', f"{fx.get('JPY', 'N/A'):.2f}" if 'JPY' in fx else 'N/A', 'N/A'))
        indicators.append(('USD/CNY', f"{fx.get('CNY', 'N/A'):.2f}" if 'CNY' in fx else 'N/A', 'N/A'))
    except Exception:
        indicators += [('USD/KRW', 'N/A', 'N/A'), ('EUR/USD', 'N/A', 'N/A'),
                       ('USD/JPY', 'N/A', 'N/A'), ('USD/CNY', 'N/A', 'N/A')]

    # 2. Twelve Data API (지수류)
    twelve_key = "6738806de23947278a07358b05e17d19"
    td_symbols = {
        "DXY": "DXY",
        "NASDAQ": "NDX",       # corrected
        "S&P 500": "SPX",      # corrected
    }

    for name, symbol in td_symbols.items():
        try:
            url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={twelve_key}"
            r = requests.get(url).json()
            price = r.get("price") or r.get("close") or "N/A"
            change_pct = r.get("percent_change") or "N/A"
            indicators.append((name, price if price else "N/A", float(change_pct) if change_pct not in [None, "N/A"] else "N/A"))
        except:
            indicators.append((name, "N/A", "N/A"))

    # 3. 수동 링크 유지
    indicators.append(('US 10Y Treasury', 'N/A', 'N/A'))
    indicators.append(('LME Copper 3M', 'N/A', 'N/A'))
    indicators.append(('WTI', 'N/A', 'N/A'))
    indicators.append(('Brent', 'N/A', 'N/A'))

    return pd.DataFrame(indicators, columns=["Indicator", "Value", "% Change"])