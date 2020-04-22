# ============================== TO-DO
"""
o Hold on buy/sell trigger if stock just recently passed indicator threshold (e.g., RSI)
o Number of shares per trade (% based on portfolio size? diversification? price momentum?)
o Additional buy/sell triggers (50 vs. 200 SMA, MACD)
o Mechanics for auto-loading new WATCHLIST stocks (based on additional metrics: DCF, EPS | P/E, News)
o Shorts/Margin trading 
"""

# ============================== LIBRARIES 
import pandas as pd
import yfinance as yf
from objects import assetfuncs as af
import imp
imp.reload(af)

# ============================== DECLARATIONS
PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0).ticker
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
CASH_ON_HAND = PORTFOLIO.loc['CASH'].value


# ============================== ALGORITHM PARAMETERS
RSI_upper = 65
RSI_lower = 50

# ============================== SCRIPT
for ticker in WATCHLIST:
    stock = af.Asset(ticker)
    stock.get_rsi()
    rsi = stock.rsi
    print(f"{ticker}: {rsi}")

    stock_last_activity = '' 
    try: 
        stock_last_activity = STOCKS.loc[ticker].last_activity
    except:
        stock_last_activity = 'NA'
    
    if (stock_last_activity != 'buy') and (rsi < RSI_lower) and (CASH_ON_HAND > stock.price): 
        stock.buy_sell('buy', 1, STOCKS, PORTFOLIO)
    elif (stock_last_activity != 'sell') and (rsi > RSI_upper) and (stock.shares > 0): 
        stock.buy_sell('sell', stock.shares, STOCKS, PORTFOLIO)

print(STOCKS)
print(PORTFOLIO)

WRITER = pd.ExcelWriter('portfolio.xlsx')
for df, sheet in zip([WATCHLIST, STOCKS, PORTFOLIO], ['watchlist', 'stocks','portfolio']):
    df.to_excel(WRITER, sheet_name = sheet)
WRITER.save()
