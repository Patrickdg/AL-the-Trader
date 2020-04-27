# TO-DO
"""
x Hold on buy/sell trigger if stock just recently passed indicator threshold (e.g., RSI)
x Update portfolio stock value 
x Split trade funcs (gather ticker data, check triggers, write to excel)
o Number of shares per trade (% based on portfolio size? diversification? price momentum?)
o Task scheduler
- Auto-email: 
    x Initial build & send
    x Trade execution, portfolio value df formatting
    o EOD email trigger
o Bugs: 
    x Sheets not updating during trade execution
"""

# LIBRARIES 
from datetime import datetime
from objects import assetfuncs as af
from objects import algofuncs as alg
from objects.algofuncs import EMAIL_ADDRESS, EMAIL_PASSWORD 
from objects.algofuncs import PORTFOLIO, WATCHLIST, STOCKS, TRADES, CASH_ON_HAND
import imp
imp.reload(alg)
imp.reload(af)

# SCRIPT
for ticker in WATCHLIST:
    asset_pkg = alg.initialize_asset(ticker, ['rsi'], STOCKS, PORTFOLIO)
    asset = asset_pkg[0]

    buy_sell = alg.determine_trade(asset_pkg)
    print(f"RSI: {asset.rsi}")
    n = 1

    if buy_sell != 'hold':
        alg.execute_trade(asset, buy_sell, n, STOCKS, PORTFOLIO)
        TRADES = alg.update_trades_df(asset, buy_sell, n, TRADES)
    elif buy_sell == 'hold' and asset.shares > 0:
        asset.update_stocks(STOCKS)
        STOCKS.loc[asset.ticker, 'current_price'] = asset.price 
        STOCKS.loc[asset.ticker, 'value'] = asset.price * asset.shares

PORTFOLIO.loc['STOCKS'].value = STOCKS.value.sum()
alg.update_workbook(WATCHLIST, STOCKS, PORTFOLIO, TRADES)

# SUMMARY EMAIL
##Extract today's trades
current_dt = datetime.now()
day = current_dt.strftime("%d/%m/%Y")
trades_executed = TRADES.loc[TRADES.date.str[0:10] == day]

# Add total column to PORTFOLIO df
PORTFOLIO.loc['Total'] = PORTFOLIO.value.sum()
alg.send_email(trades_executed, STOCKS, PORTFOLIO)

# TESTING
# print(PORTFOLIO)
# print(STOCKS)
# print(TRADES)
