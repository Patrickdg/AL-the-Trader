import pandas as pd

def majority_buy_sell(close_prices, periods = [5, 10, 20]):
    close_prices.rolling
    '''
    Calculate max/min windows for each closing price: 
    - if equal to max, then sell, if equal to min, then buy, else hold
    - calculate for 7, 11, and 21 day periods
    - if 2 or more indicators indicate buy/sell, then label buy/sell
    '''