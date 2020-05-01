# TO-DO
"""
x Hold on buy/sell trigger if stock just recently passed indicator threshold (e.g., RSI)
x Update portfolio stock value 
x Split trade funcs (gather ticker data, check triggers, write to excel)
x Number of shares per trade (% based on portfolio size? diversification? price momentum?)
x Task scheduler
- Auto-email: 
    x Initial build & send
    x Trade execution, portfolio value df formatting
    o EOD email trigger
x Bugs: 
"""

# LIBRARIES 
from datetime import datetime
from objects import assetfuncs as af
from objects import algofuncs as alg
from objects.algofuncs import EMAIL_ADDRESS, EMAIL_PASSWORD 
from objects.algofuncs import PORTFOLIO, PORTFOLIO_HIST, WATCHLIST, STOCKS, TRADES, CASH_ON_HAND
import imp
imp.reload(alg)
imp.reload(af)

# MAIN
for ticker in WATCHLIST:
    # Initialize asset
    asset = alg.initialize_asset(ticker, STOCKS)

    print(asset.ticker)
    print(f"RSI: {asset.rsi}")
    print(f"Price: {asset.price}")

    # Check triggers & determine action
    order = alg.check_indicators(asset, ['rsi']) #buy, sell, or neutral
    num_shares = alg.buyable_shares(asset.price, CASH_ON_HAND)  # TEMPORARY: num shares to buy

    if order != 'neutral': 
        # Check if portfolio contains enough cash/shares to buy/sell, and last activity
        tradable = alg.check_tradable(asset, order, num_shares, STOCKS, PORTFOLIO)
        if tradable:
            trade = alg.execute_trade(asset, order, num_shares, STOCKS, PORTFOLIO, TRADES)
            TRADES = TRADES.append(trade, ignore_index = True)
            PORTFOLIO.loc['CASH'].value -= asset.cash_change
            # Update STOCKS df to remove unowned tickers, or update with new values
            if asset.shares == 0: 
                STOCKS.drop(asset.ticker, inplace = True)
        else:
            print(f"{asset.ticker}: Hold at {asset.price}\n")
    else:
        print(f"{asset.ticker}: Hold at {asset.price}\n")

    if asset.shares > 0: 
        STOCKS.loc[asset.ticker] = asset.compiled
# Update dfs
current_date = datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")

PORTFOLIO.loc['STOCKS'].value = STOCKS.value.sum()
PORTFOLIO.loc['TOTAL'] = sum([PORTFOLIO.loc['CASH'].value,
                              PORTFOLIO.loc['STOCKS'].value])
PORTFOLIO_HIST.loc[current_date] = PORTFOLIO.transpose().values[0]
alg.update_workbook(WATCHLIST, STOCKS, PORTFOLIO, TRADES, PORTFOLIO_HIST)

# SUMMARY EMAIL
trades_executed = alg.todays_trades(TRADES)
alg.send_email(trades_executed, STOCKS, PORTFOLIO)

# # TESTING
# print(PORTFOLIO)
# print(STOCKS)
# print(TRADES)
