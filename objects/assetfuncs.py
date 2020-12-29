# LIBRARIES 
import numpy as np
import pandas as pd
import yfinance as yf

# OBJECTS
class Asset():
    def __init__(self, ticker):
        self.data = yf.Ticker(ticker)
        self.all_history = self.data.history(period = '1y').Close
        
        #Price values; updated each trading day via self.update_history_subset()
        self.ticker = ticker
        self.history = self.all_history
        self.price = self.history[-1]
        self.prev = self.history[-2]
        self.trend = round(((self.price / self.prev) - 1) * 100, 4)

        self.shares = 0 # shares held in portfolio
        self.purch_price = ''
        self.last_activity = ''

        self.rsi = calc_rsi(self.history)
        self.compiled = []
        self.cash_change = 0

    def get_current_holdings(self, stocks_df):
        if self.last_activity == '':
            try:
                self.purch_price = stocks_df.loc[self.ticker].purch_price
                self.shares = stocks_df.loc[self.ticker].shares
                self.last_activity = stocks_df.loc[self.ticker].last_activity
            except KeyError:
                self.purch_price = 'NA'
                self.shares = 0
                self.last_activity = 'NA'

    def update_compile(self):
        self.compiled = [
                    self.purch_price,
                    self.price,
                    self.shares,
                    self.price * self.shares,
                    self.rsi, 
                    self.last_activity
                    ]

    def update_values(self, stocks_df):
        self.get_current_holdings(stocks_df)
        self.update_compile()

    def get_history_subset(self, start_date, end_date): 
        return self.all_history.loc[start_date : end_date]

    def update_history_subset(self, start_date, end_date):
        self.history = self.get_history_subset(start_date, end_date)
        self.price = self.history[-1]
        self.prev = self.history[-2]
        self.trend = round(((self.price / self.prev) - 1) * 100, 4)

        self.rsi = calc_rsi(self.history)
        
    def get_rsi(self, period = 10, avg_method = 'sma'):
        self.rsi = calc_rsi(self.history, period, avg_method)
        
    def buy_sell(self, buy_sell, num_shares):
        if buy_sell == 'sell': 
            num_shares *= -1
        cash_change = float(num_shares) * self.price
        
        self.shares += num_shares
        self.last_activity = buy_sell
        self.purch_price = self.price
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

def calc_rs(historicals, lookback_period = 10, avg_method = 'sma'):
    historicals = historicals[-(lookback_period+1):]
    delta = historicals.diff()
    
    u_changes = delta[delta > 0]
    d_changes = delta[delta < 0].map(abs)

    u_avg = sum(u_changes)/lookback_period
    d_avg = sum(d_changes)/lookback_period

    try:
        rs = u_avg / d_avg
    except ZeroDivisionError:
        rs = u_avg/0.0000001
    return rs

def calc_rsi(data, lookback_period = 10, avg_method = 'sma'):
    relative_strength = calc_rs(data, lookback_period, avg_method)
    
    rsi = 100 - (100 / (1 + relative_strength))
    return rsi
