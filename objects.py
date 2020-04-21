# LIBRARIES ==============================
import yfinance as yf
import pandas as pd

# OBJECTS, FUNCTIONS ==============================
class Asset():
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = 0
        self.shares = 0
        self.history = 0
        self.dict = {}
        self.rsi = 0

    def get_ticker_data(self, period = '2mo'):
        data = yf.Ticker(self.ticker)
        history = data.history(period = period).Close[-1]
        self.history = history
        self.price = history[-1]

    def get_portfolio_data(self, df):
        self.shares = df.loc[df.ticker == self.ticker].shares

    def buy(self, portfolio_df):
        self.compile_dict()

    def sell(self):
        pass

    def rsi(self):
        pass

    def compile_dict(self):
        self.dict = {'ticker': self.ticker,
                    'current_price': self.price,
                    'shares': self.shares,
                    'value': self.price * self.shares,
                    'current_rsi': self.rsi}

def calc_rsi():
    pass