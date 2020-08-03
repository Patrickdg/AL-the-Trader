'''
For each stock in watchlist, gather stock price + volume data + rolling aggregates
'''

#LIBRARIES
import pandas as pd
import numpy as np
import yfinance as yf
import ml.rolling_agg_funcs as ra

import imp
imp.reload(ra)

#DECLARATIONS/PARAMS
watchlist = pd.read_excel('ml/watchlist_ml.xlsx', sheet_name = 'watchlist')
period = '5y' # for individual stock history
cols = ['Open','High','Low','Close','Volume']
drop_cols = ['Dividends', 'Stock Splits']
periods = [5, 10, 15, 21, 130, 260] # for rolling aggregate calcs
funcs = [ra.rolling_mean, ra.rolling_max, ra.rolling_min, ra.rolling_stdev, ra.z_score]
benchmark_ticker = 'VTSMX' # The Vanguard Total Stock Market Index 

#SET BENCHMARK INDEX
benchmark_history = yf.Ticker(benchmark_ticker).history(period = period)
benchmark_history = ra.add_rolling_cols(benchmark_history, cols, periods, funcs).drop(drop_cols, axis = 1)
benchmark_history.columns = [f'market_{col}' for col in benchmark_history.columns]

# MAIN LOOP
assets = pd.DataFrame() 
for ticker in watchlist.ticker: 
    # Initialize asset history
    asset = yf.Ticker(ticker)
    asset_figs = asset.history(period = period)
    # Add Rolling columns + indicators
    asset_figs = ra.add_rolling_cols(asset_figs, cols, periods, funcs).drop(drop_cols, axis = 1)

    # JOIN: Benchmark info
    asset_figs = pd.merge(asset_figs, benchmark_history, on = 'Date')

    # Calculate growth rates, concat with original figs and ticker info
    deltas = asset_figs.diff()/asset_figs.shift(1)
    deltas.columns = [f'{col}_delta' for col in deltas.columns]

    asset_figs = pd.concat([asset_figs[cols],
                            asset_figs.iloc[:, ['z_score' in col for col in asset_figs.columns]],
                            deltas], 
                            axis = 1)
    asset_figs['sector'] = asset.info['sector']

    assets = pd.concat([assets, asset_figs]); print(assets.shape)
    print(ticker)
    # if ticker == 'WMT': 
    break
# Drop all Nan columns, Reorder columns
assets.dropna(how = 'all', axis = 1, inplace = True); assets.dropna(how = 'any', axis = 0, inplace = True)
assets.reset_index(inplace = True)

first_cols = ['Date','sector']; rem_cols = [col for col in assets.columns if col not in first_cols]
assets = assets[first_cols+rem_cols]

# assets.to_excel('ml/consolidated_asset_stock.xlsx')