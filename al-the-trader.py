#==============================
# Libraries
import pandas as pd
import yfinance as yf

# PARAMETERS ==============================
PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0)

# TESTING ==============================
msft = yf.Ticker("MSFT")

msft.info
msft.quarterly_cashflow
msft.quarterly_balance_sheet
msft.earnings
msft.sustainability
msft.history(period = '2wk')
msft.actions

