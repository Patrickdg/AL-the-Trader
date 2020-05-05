# LIBRARIES 
import numpy as np
import pandas as pd
import yfinance as yf

# OBJECTS
class Asset():
    def __init__(self, ticker, period = '2mo'):
        data = yf.Ticker(ticker)
        
        self.ticker = ticker
        self.history = data.history(period = period).Close
        self.price = data.history(period = period).Close[-1]
        self.prev = data.history(period = period).Close[-2]
        self.trend = round(((self.price / self.prev) - 1) * 100, 4)
        self.shares = 0 # shares held in portfolio
        self.rsi = calc_rsi(self.history)
        self.last_activity = ''
        self.compiled = []
        self.cash_change = 0

    def get_current_holdings(self, stocks_df):
        if self.last_activity == '':
            try:
                self.shares = stocks_df.loc[self.ticker].shares
                self.last_activity = stocks_df.loc[self.ticker].last_activity
            except KeyError:
                self.shares = 0
                self.last_activity = 'NA'

    def update_compile(self):
        self.compiled = [
                    self.price,
                    self.shares,
                    self.price * self.shares,
                    self.rsi, 
                    self.last_activity
                    ]

    def update_values(self, stocks_df):
        self.get_current_holdings(stocks_df)
        self.update_compile()
        
    def get_rsi(self, period = 14, avg_method = 'sma'):
        self.rsi = calc_rsi(self.history, period, avg_method)
        
    def buy_sell(self, buy_sell, num_shares):
        if buy_sell == 'sell': 
            num_shares *= -1
        cash_change = float(num_shares) * self.price
        
        self.shares += num_shares
        self.last_activity = buy_sell
        self.cash_change = cash_change

        self.update_compile()

        print(f"{self.ticker}: Order executed to {buy_sell} {num_shares} share(s) at {self.price}\n")

# INDICATOR FUNCTIONS
##RSI
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

    historicals = historicals[-lookback_period+1:]
    for n in range(1, len(historicals)):
        chg = round(historicals[n] - historicals[n-1], 4)
        if chg > 0: 
            u_changes.append(chg)
        elif chg < 0: 
            d_changes.append(abs(chg))
    u_len = len(u_changes)
    d_len = len(d_changes)

    print(u_changes)
    print(d_changes)

    u_avg = ''
    d_avg = ''
    if avg_method == 'sma':
        u_avg = calc_sma(u_changes, u_len)
        d_avg = calc_sma(d_changes, d_len)
    elif avg_method == 'ema':
        u_avg = calc_ema(u_changes, u_len)
        d_avg = calc_ema(d_changes, d_len)

    print(u_avg)
    print(d_avg)
    rs = u_avg / d_avg
    print(f"rs = {rs}")
    return rs

def calc_rsi(data, lookback_period = 14, avg_method = 'sma'):
    relative_strength = calc_rs(data, lookback_period, avg_method)
    
    rsi = 100 - (100 / (1 + relative_strength))
    return rsi

x = asset.history
calc_rs(x, 14, 'sma')
calc_rsi(x, 14, 'sma')