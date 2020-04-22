# LIBRARIES ==============================
import yfinance as yf
import pandas as pd
import numpy as np

# OBJECTS, FUNCTIONS ==============================
class Asset():
    def __init__(self, ticker, period = '2mo'):
        data = yf.Ticker(ticker)
        
        self.ticker = ticker
        self.history = data.history(period = period).Close
        self.price = data.history(period = period).Close[-1] # extract latest price
        self.shares = 0 # shares held in portfolio
        self.rsi = 0

    def get_portfolio_data(self, df):
        self.shares = df.loc[df.ticker == self.ticker].shares

    def buy_sell(self, buy_sell, num_shares, stocks_df, portfolio_df):
        if buy_sell == 'sell': 
            num_shares *= -1
        cash_change = num_shares * self.price
        
        self.update_portfolio(cash_change, portfolio_df)
        self.update_stocks(stocks_df)
        self.shares += num_shares

    def update_portfolio(self, cash_change, portfolio_df):
        portfolio_df.xs('CASH')['value'] -= cash_change
        portfolio_df.xs('STOCKS')['value'] += cash_change

    def update_stocks(self, stocks_df):
        asset = compile_asset()
        stocks_df.loc[self.ticker] = asset

    def compile_asset(self):
        asset = [self.ticker,
                self.price,
                self.shares,
                self.price * self.shares,
                self.rsi
                ]
        return asset

    def rsi(self):
        pass

# REFERENCE LINK FOR AVERAGES (https://www.macroption.com/rsi-calculation/)
def calc_sma(historicals, periods):
    period = historicals[-periods:]
    return np.mean(period)

def calc_ema(historicals, periods):
    alpha = (2 / (periods + 1))
    n = historicals[-1]
    avg_excl_n = np.mean(historicals[-periods:-1])

    return (alpha * n) + (1 - alpha) * avg_excl_n

def calc_rs(historicals, lookback_period, avg_method):
    u_changes = []
    d_changes = []

    historicals = historicals[-lookback_period:]
    for n in range(1, len(historicals)):
        chg = historicals[n] - historicals[n-1]
        if chg > 0: 
            u_changes.append(chg)
        elif chg < 0: 
            d_changes.append(abs(chg))
    
    u_len = len(u_changes)
    d_len = len(d_changes)

    u_avg = ''
    d_avg = ''
    if avg_method == 'sma':
        u_avg = calc_sma(u_changes, u_len-1)
        d_avg = calc_sma(d_changes, d_len-1)
    elif avg_method == 'ema':
        u_avg = calc_ema(u_changes, u_len-1)
        d_avg = calc_ema(d_changes, d_len-1)

    rs = u_avg / d_avg
    return rs

def calc_rsi(data, lookback_period, avg_method):
    relative_strength = calc_rs(data, lookback_period, avg_method)
    
    rsi = 100 - (100 / (1 + relative_strength))
    return rsi

# TESTING ==============================
msft = yf.Ticker("MSFT")

x = msft.history(period = '3wk')
# calc_rsi(x.Close, 14, 'ema')

