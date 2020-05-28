# LIBRARIES
import inspect, os
import pandas as pd
from datetime import datetime
from collections import Counter
import math

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from objects import assetfuncs as af
import imp
imp.reload(af)


# DECLARATIONS
##SHEETS
PORTFOLIO_FILE = pd.ExcelFile('portfolio.xlsx')
PORTFOLIO = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'portfolio', header = 0, index_col = 0)
PORTFOLIO_HIST = pd.read_excel(PORTFOLIO_FILE, sheet_name = 'summary', header = 0, index_col = 0)
WATCHLIST = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'watchlist', header = 0, index_col = 0)
STOCKS = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'stocks', header = 0, index_col = 0)
TRADES = pd.read_excel(PORTFOLIO_FILE, sheet_name= 'trades', header = 0, index_col = 0)
CASH_ON_HAND = PORTFOLIO.loc['CASH'].value

##EMAIL
EMAIL_ADDRESS = os.environ.get('AL_EMAIL')
EMAIL_PASSWORD = os.environ.get('AL_PASS')


# FUNCTIONS
def initialize_asset(ticker, stocks_df):
    asset = af.Asset(ticker)
    asset.update_values(stocks_df)
    return asset

def check_indicators(asset, indicators):
    # Returns final 'buy' or 'sell' command from indicators
    # Update dict to include any new indicators (SMA, MACD, BB, etc.)
    # Format: 'indicator': [check_ind()]
    indicator_dict = {'rsi': check_rsi(asset.rsi)} 
    
    indicator_orders = {}
    for ind in indicators: 
        buy_sell = indicator_dict[ind]
        indicator_orders[ind] = buy_sell 
    
    orders = indicator_orders.values()
    order, count = Counter(orders).most_common()[0]
    return order

# TRADE FUNCTION 
def buyable_shares(asset_price, cash_on_hand):
    num_shares = 0
    maximum = 0.1 * cash_on_hand
    if asset_price < maximum:
        num_shares = math.floor(maximum/asset_price)
    else:
        num_shares = 1
    return num_shares

def check_tradable(asset, buy_sell, num_shares, stocks_df, portfolio_df):
    tradable = ''
    cash_available = ''
    last_activity = asset.last_activity

    if portfolio_df.loc['CASH'].value > asset.price*num_shares:
        cash_available = True
    else: 
        cash_available = False

    if buy_sell == 'buy' and cash_available and last_activity != 'buy': 
        tradable = True
    elif buy_sell == 'sell' and asset.shares >= num_shares and last_activity != 'sell': 
        tradable = True

    return tradable

def execute_trade(asset, buy_sell, num_shares, stocks_df, portfolio_df, trades_df):
    # @ asset-level
    asset.buy_sell(buy_sell, num_shares) 
    # @ portfolio-level
    trade_date = datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")
    shares_value = asset.price * num_shares
    executed = pd.Series([trade_date, asset.ticker, buy_sell, num_shares, shares_value], index = trades_df.columns)
    return executed 

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

# OTHER FUNCTIONS
##TODAY'S TRADES
def todays_trades(trades_df):
    current_dt = datetime.now()
    day = current_dt.strftime("%d/%m/%Y")
    trades_executed = trades_df.loc[trades_df.date.str[0:10] == day]
    return trades_executed

##EXCEL
def update_workbook(watchlist, stocks_df, portfolio_df, trades_df, portfolio_hist):
    writer = pd.ExcelWriter('portfolio.xlsx')
    dfs = [watchlist, stocks_df, portfolio_df, trades_df, portfolio_hist]
    sheet_names = ['watchlist', 'stocks','portfolio', 'trades', 'summary']

    for df, sheet in zip(dfs, sheet_names):
        df.to_excel(writer, sheet_name = sheet)

    writer.save()

##EMAIL
def send_email(trades_df, stocks_df, portfolio_df):
    sender = EMAIL_ADDRESS
    password = EMAIL_PASSWORD
    server = 'smtp.gmail.com:587'
    recipient = 'deguzmap20@gmail.com'

    text = f"""
    AL here! 

    Here is a summary of the last EXECUTED TRADES:

    {trades_df}

    CURRENT HOLDINGS: 

    {stocks_df}

    PORTFOLIO SUMMARY:

    {portfolio_df}
  
    - AL
    """

    html = f"""
    <html><body><p>AL here!</p>
    <p>Here is a summary of the last EXECUTED TRADES:</p>
    {trades_df.to_html()}
    <p>CURRENT HOLDINGS:</p>
    {stocks_df.to_html()}
    <p>PORTFOLIO SUMMARY:</p>
    {portfolio_df.to_html()}
    <p>- AL</p>
    </body></html>
    """

    # text = text.format(table=df)
    # html = html.format(table=df)
    message = MIMEMultipart(
        "alternative", None, [MIMEText(text), MIMEText(html,'html')])

    message['Subject'] = f"Trading Summary - {datetime.now()}"
    message['From'] = sender
    message['To'] = recipient

    server = smtplib.SMTP(server)
    server.ehlo()
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, message.as_string())

    server.quit()