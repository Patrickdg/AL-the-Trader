# LIBRARIES
import os
import smtplib
import pandas as pd
from datetime import datetime
from collections import Counter
from objects import assetfuncs as af
import imp
imp.reload(af)

# DECLARATIONS
EMAIL_ADDRESS = os.environ.get('AL_EMAIL')
EMAIL_PASSWORD = os.environ.get('AL_PASS')

PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0).ticker
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
TRADES = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'trades', header = 0)
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
def determine_trade(asset_package):
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
    
    return buy_sell

def execute_trade(asset, buy_sell, n, stocks_df, portfolio_df):
    asset.buy_sell(buy_sell, n, stocks_df, portfolio_df)
    print(f"{asset.ticker}: Order executed to {buy_sell} {n} share(s) at {asset.price}")

def update_trades_df(asset, buy_sell, n, trades_df):
    trade_date = datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")
    shares_value = asset.price * n
    new_trade = pd.Series([trade_date, asset.ticker, buy_sell, n, shares_value], index = trades_df.columns)

    return trades_df.append(new_trade, ignore_index = True)    

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


# OTHER FUNCTIONS

##EXCEL
def update_workbook(watchlist, stocks_df, portfolio_df, trades_df):
    writer = pd.ExcelWriter('portfolio.xlsx')
    dfs = [watchlist, stocks_df, portfolio_df, trades_df]
    sheet_names = ['watchlist', 'stocks','portfolio', 'trades']

    for df, sheet in zip(dfs, sheet_names):
        df.to_excel(writer, sheet_name = sheet)

    writer.save()

##EMAIL
def send_email(email):
    email_df_format()
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    subject = email['subject']
    body = email['body']

    to_send = f'Subject: {subject}\n\n{body}'

    smtp.sendmail(EMAIL_ADDRESS, 'deguzmap20@gmail.com', to_send)
    smtp.quit()

def email_df_format():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
    pd.options.display.max_rows