# TO-DO
"""
x Hold on buy/sell trigger if stock just recently passed indicator threshold (e.g., RSI)
o Split trade funcs (gather ticker data, check triggers, write to excel)
o Number of shares per trade (% based on portfolio size? diversification? price momentum?)
o Task schedule
o Auto-email: Trade execution, portfolio value, relevant stock news
o Bugs: 
    o RSI calcs?
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
    asset = alg.initialize_asset(ticker, ['rsi'], STOCKS, PORTFOLIO)
    print(f"RSI: {asset[0].rsi}")
    alg.determine_execute_trade(asset)

print(STOCKS)
print(PORTFOLIO)

alg.update_workbook(WATCHLIST, STOCKS, PORTFOLIO, TRADES)


# TESTING
# asset[0].update_trades('buy', 1, TRADES)

# import pandas as pd
# from datetime import datetime
# trade_date = datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")
# test = pd.Series([trade_date, asset[0].ticker, 'buy', 1, 1*asset[0].price], index = TRADES.columns)
# TRADES.append(test, ignore_index = True)