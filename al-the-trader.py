# TO-DO
"""
x Hold on buy/sell trigger if stock just recently passed indicator threshold (e.g., RSI)
o Split trade funcs (gather ticker data, check triggers, write to excel)
o Number of shares per trade (% based on portfolio size? diversification? price momentum?)
o Task schedule
o Auto-email: Trade execution, portfolio value, relevant stock news
o Bugs: 
    o RSI calcs?
    x Sheets not updating during trade execution
"""

# LIBRARIES 
from objects import assetfuncs as af
from objects import algofuncs as alg
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

print(PORTFOLIO)
print(STOCKS)
print(TRADES)

alg.update_workbook(WATCHLIST, STOCKS, PORTFOLIO, TRADES)
