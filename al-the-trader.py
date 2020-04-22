# ============================== LIBRARIES 
import pandas as pd
import yfinance as yf
import asset_funcs as af

# ============================== PARAMETERS
PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0).ticker
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
CASH_ON_HAND = PORTFOLIO.loc['CASH'].value

# ============================== SCRIPT
for ticker in WATCHLIST:
    stock = af.Asset(ticker)
    print(ticker)
    print(stock.price)
    stock.get_rsi()
    stock.get_current_holdings()
    rsi = stock.rsi
    print(rsi)

    if rsi < 35 and CASH_ON_HAND > stock.price: 
        stock.buy_sell('buy', 1, STOCKS, PORTFOLIO)
    elif rsi > 65 and stock.shares > 0 : 
        stock.buy_sell('sell', 1, STOCKS, PORTFOLIO)

print(STOCKS)
print(PORTFOLIO)

# ============================== TESTING
# msft = yf.Ticker("MSFT")

# msft.info
# msft.quarterly_cashflow
# msft.quarterly_balance_sheet
# msft.earnings
# msft.sustainability
# x = msft.history(period = '3wk')
# msft.actions
# msft.institutional_holders
# msft.insider

