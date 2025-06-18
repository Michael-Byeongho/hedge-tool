import requests
import pandas as pd

def get_macro_data():
    api_key = "6738806de23947278a07358b05e17d19"
    symbols = {
        'USD/KRW': 'USD/KRW',
        'EUR/USD': 'EUR/USD',
        'USD/JPY': 'USD/JPY',
        'USD/CNY': 'USD/CNY',
        'DXY': 'DXY',
        'NASDAQ': 'IXIC',
        'S&P 500': 'GSPC',
        'WTI': 'CL=F',
        'Brent': 'BZ=F'
    }

    results = []
    for name, symbol in symbols.items():
        try:
            resp = requests.get(f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}").json()
            price = float(resp['price'])
        except:
            price = "N/A"

        results.append({'Indicator': name, 'Value': price, 'Change (%)': "N/A"})

    results.append({'Indicator': 'US 10Y Treasury', 'Value': 'N/A', 'Change (%)': 'N/A'})
    results.append({'Indicator': 'LME Copper 3M', 'Value': 'N/A', 'Change (%)': 'N/A'})

    df = pd.DataFrame(results)
    return df