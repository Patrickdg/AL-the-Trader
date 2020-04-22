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
RSI_lower = 35

# ============================== SCRIPT
for ticker in WATCHLIST:
    stock = af.Asset(ticker)
    stock.get_rsi()
    rsi = stock.rsi

    if rsi < RSI_lower and CASH_ON_HAND > stock.price: 
        stock.buy_sell('buy', 1, STOCKS, PORTFOLIO)
    elif rsi > RSI_upper and stock.shares > 0: 
        stock.buy_sell('sell', 1, STOCKS, PORTFOLIO)

print(STOCKS)
print(PORTFOLIO)

