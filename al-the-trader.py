# NOTES
"""
"AL" currently trades on a simple Relative Strength Index (RSI) trigger (30 buy, 70 sell)
with a simple moving average (SMA) and shortened lookback period of 10 days. 

Current watchlist contains the 30 stocks in the DJIA, as of May 1, 2020. 

- Backdating
    - run check to build list of days that trading did not run  
    - iterate over each day, run trading logic  
        --> initialize portfolios/assets
        --> for day in trading_days: 
            --> for ticker in portfolio: 
                --> run trading sim  
                --> update portfolio and gsheet
"""

# LIBRARIES 
import pandas as pd
from datetime import datetime, timedelta
from objects import assetfuncs as af
from objects import algofuncs as alg
from objects.algofuncs import PORTFOLIO, PORTFOLIO_HIST, WATCHLIST, STOCKS, TRADES, CASH_ON_HAND

# DECLARATIONS
testing = False
lookback_period = 60
current_date = datetime.now()
last_trading_day = datetime.strptime(PORTFOLIO_HIST.index[-1], "%d/%m/%Y %H:%M:%S")
missed_trading_days = pd.bdate_range(last_trading_day, current_date, normalize = True)

# MAIN
## Initialize assets
ASSETS = []
for ticker in WATCHLIST.index:
    asset = alg.initialize_asset(ticker, STOCKS)
    ASSETS.append(asset)

## Run backdating
for trading_day in missed_trading_days: 
    # Set stock price window per trading_day
    start_date = trading_day - timedelta(days = lookback_period)

    for asset in ASSETS:
        # Update stock values to reflect current trading day
        asset.update_history_subset(start_date = start_date, end_date = trading_day)

        # Check triggers & determine action
        order = alg.check_indicators(asset, ['rsi']) #buy, sell, or neutral
        num_shares = alg.buyable_shares(asset.price, CASH_ON_HAND)

        # Update WATCHLIST df: price, trend (% change), indicator values
        WATCHLIST = alg.update_port_ticker_values(WATCHLIST, ticker, asset)

        if order != 'neutral': 
            # Check if portfolio contains enough cash/shares to buy/sell, and last activity
            tradable = alg.check_tradable(asset, order, num_shares, STOCKS, PORTFOLIO)
            if tradable:
                num_shares = asset.shares if order == 'sell' else num_shares # sell all shares, buy only buyable 
                trade = alg.execute_trade(trading_day, asset, order, num_shares, STOCKS, PORTFOLIO, TRADES)
                TRADES = TRADES.append(trade, ignore_index = True)
                PORTFOLIO.loc['CASH'].value -= asset.cash_change
                # Update STOCKS df to remove unowned tickers, or update with new values
                if asset.shares == 0 or asset.shares == 'NaN': 
                    STOCKS.drop(asset.ticker, inplace = True)
            else:
                print(f"{asset.ticker}: Hold at {asset.price} on {trading_day}\n")
        else:
            print(f"{asset.ticker}: Hold at {asset.price} on {trading_day}\n")

        if asset.shares > 0: 
            STOCKS.loc[asset.ticker] = asset.compiled

    # Update dfs
    STOCKS = alg.update_holdings_values(STOCKS, ASSETS)
    PORTFOLIO.loc['STOCKS'].value = STOCKS.value.sum()
    PORTFOLIO.loc['TOTAL'] = sum([PORTFOLIO.loc['CASH'].value,
                                PORTFOLIO.loc['STOCKS'].value])
    PORTFOLIO_HIST = PORTFOLIO_HIST.loc[PORTFOLIO_HIST.index.str[0:10] != trading_day.strftime("%d/%m/%Y")]
    PORTFOLIO_HIST.loc[trading_day.strftime("%d/%m/%Y %H:%M:%S")] = PORTFOLIO.transpose().values[0]
    WATCHLIST.sort_values(by = 'rsi', inplace = True)

if not testing: 
    from objects import updatefuncs as uf
    from objects.algofuncs import EMAIL_ADDRESS, EMAIL_PASSWORD 
    from objects.updatefuncs import GS_WORKBOOK

    #UPDATE: EXCEL
    alg.update_workbook('portfolio.xlsx', WATCHLIST, STOCKS, PORTFOLIO, TRADES, PORTFOLIO_HIST)
    #UPDATE: GOOGLE SHEETS
    sheet_names_list = ['watchlist','stocks','portfolio','trades','summary']
    df_list = [WATCHLIST, STOCKS, PORTFOLIO, TRADES, PORTFOLIO_HIST]

    try:
        for name, df in zip(sheet_names_list, df_list): 
            uf.update_gs_workbook(GS_WORKBOOK, name, df) 
    except Exception as error: 
        print(f'FAILED TO UPDATE GOOGLE SHEET: {str(error)}')

    # SUMMARY EMAIL
    if current_date.hour >= 16:
        trades_executed = alg.todays_trades(TRADES)
        alg.send_email(trades_executed, STOCKS, PORTFOLIO)
elif testing: 
    alg.update_workbook('__testing/portfolio.xlsx', WATCHLIST, STOCKS, PORTFOLIO, TRADES, PORTFOLIO_HIST)
