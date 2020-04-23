# LIBRARIES
import pandas as pd
from collections import Counter
from objects import assetfuncs as af
import imp
imp.reload(af)

# DECLARATIONS
PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0).ticker
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
CASH_ON_HAND = PORTFOLIO.loc['CASH'].value

# FUNCTIONS
def initialize_asset(ticker, indicators, stocks_df, portfolio_df):
    asset = af.Asset(ticker)

    stock_last_activity = get_last_activity(ticker, stocks_df)
    indicator_vals = check_indicators(asset, indicators)
    buy_sell_inds = check_buy_sell(indicator_vals)

    asset_package = [asset, 
                    stock_last_activity, 
                    indicator_vals, 
                    buy_sell_inds]
    
    return asset_package

def get_last_activity(ticker, stocks_df):
    stock_last_activity = ''
    try: 
        stock_last_activity = stocks_df.loc[ticker].last_activity
    except:
        stock_last_activity = 'NA'

    return stock_last_activity

def check_indicators(asset, indicators):
    # Update dict to include any new indicators (SMA, MACD, BB, etc.)
    # Format: 'indicator': [asset.calculation, asset.indicator_value, check_ind_function()]
    indicator_dict = {'rsi': [asset.get_rsi(), check_rsi(asset.rsi)]} 
    
    indicator_vals = {}
    for ind in indicators: 
        indicator_dict[ind][0] # calculate indicator value
        buy_sell = indicator_dict[ind][1] # use appropriate check_indicator function
        indicator_vals[ind] = buy_sell 
    
    return indicator_vals

def check_buy_sell(indicators_dict):
    vals = indicators_dict.values()
    val, count = Counter(vals).most_common()[0]
    return val

# TRADE FUNCTION 
def execute_trade(asset, buy_sell, n, stocks_df, portfolio_df):
    asset.buy_sell(buy_sell, n, stocks_df, portfolio_df)
    print(f"{asset.ticker}: Order executed to {buy_sell} {n} share(s) at {asset.price}")
    
def determine_execute_trade(asset_package):
    asset = asset_package[0]
    cash_available = True if CASH_ON_HAND > asset.price else False
    stock_last_activity = asset_package[1]
    buy_sell_inds = asset_package[3]

    buy_sell = ''
    if stock_last_activity != 'buy' and buy_sell_inds == 'buy' and cash_available:
        buy_sell = 'buy'
    elif stock_last_activity != 'sell' and buy_sell_inds == 'sell' and asset.shares > 0:
        buy_sell = 'sell'
    else: 
        buy_sell = 'hold'
        print(f"{asset.ticker}: HOLD {asset.shares}")

    if buy_sell in ['buy', 'sell']:
        execute_trade(asset, buy_sell, 1, STOCKS, PORTFOLIO)

# INDICATOR FUNCTIONS
##RSI
def check_rsi(rsi, min_max = [30,70]): 
    buy_sell = 'neutral'
    if rsi < min_max[0]: 
        buy_sell = 'buy'
    elif rsi > min_max[1]:
        buy_sell = 'sell'
    else:
        pass

    return buy_sell

##50SMA - 200SMA


# EXCEL FUNCTIONS
def update_workbook(watchlist, stocks_df, portfolio_df):
    writer = pd.ExcelWriter('portfolio.xlsx')
    for df, sheet in zip([watchlist, stocks_df, portfolio_df], ['watchlist', 'stocks','portfolio']):
        df.to_excel(writer, sheet_name = sheet)
    writer.save()
