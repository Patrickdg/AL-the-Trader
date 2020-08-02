'''
For each stock in watchlist, gather stock price + volume data
'''

#LIBRARIES
import pandas as pd
import numpy as np
import yfinance as yf

#DECLARATIONS
watchlist = pd.read_excel('ml/watchlist_ml.xlsx', sheet_name = 'watchlist')

period = '5y'

#FUNCS
def rolling_col_mean(df, col_name, period):
    ma_col = df[col_name].rolling(period).mean()
    return ma_col
def rolling_col_max(df, col_name, period):
    ma_col = df[col_name].rolling(period).max()
    return ma_col
def rolling_col_min(df, col_name, period):
    ma_col = df[col_name].rolling(period).min()
    return ma_col

#SET BENCHMARK INDEX
benchmark_ticker = 'VTSMX' # The Vanguard Total Stock Market Index 
benchmark_history = yf.Ticker(benchmark_ticker).history(period = period)

# MAIN LOOP
assets = pd.DataFrame() 
for ticker in watchlist.ticker: 
    # Initialize asset info
    asset = yf.Ticker(ticker)
    asset_figs = asset.history(period = period)
    
    # Add Moving average columns
    for col in ['Open','High','Low','Close','Volume']:
        for n in [7, 14, 21 ,28]: 
            for func in [rolling_col_mean, rolling_col_max, rolling_col_min]:
                function = func.__name__.replace("rolling_col_", "")
                asset_figs[f'{col}_ma_{function}_{n}'] = func(asset_figs, col, n)

    # JOIN: Benchmark info

    # Calculate growth rates
    asset_figs = asset_figs.diff()/asset_figs.shift(1)

    # add ticker
    asset_figs['sector'] = asset.info['sector']


    print(ticker)
    assets = pd.concat([assets, asset_figs]); print(assets.shape)
    
# Reorder columns
assets.reset_index(inplace = True)
first_cols = ['Date','sector']; rem_cols = [col for col in assets.columns if col not in first_cols]
assets = assets[first_cols+rem_cols].reset_index(drop = True)
# assets.to_excel('ml/consolidated_asset_stock.xlsx')
