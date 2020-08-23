#LIBRARIES
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os

from objects.algofuncs import WATCHLIST
import rolling_agg_funcs as ra
import indicators as ind

import imp
imp.reload(ra)
imp.reload(ind)

#DECLARATIONS/PARAMS
periods = [5, 10, 21, 65] # for rolling aggregate calcs
period = f'{max(periods)*2+1}d' # for individual stock history
cols = ['Open','High','Low','Close', 'Volume', 'rsi', 'macd_hist', 
        'bb_upper_band', 'bb_upper_diff', 'bb_lower_band', 'bb_lower_diff']
drop_cols = ['Dividends', 'Stock Splits']
features_to_keep = pd.read_csv('ml/regression/lm_inputs/features.csv', header = None)
funcs = [ra.rolling_mean, ra.rolling_max, ra.rolling_min, ra.rolling_stdev, ra.z_score]
benchmark_ticker = 'VTSMX' # Vanguard Total Stock Market Index 

delta = 0 # DELTA FOR NUM. DAYS BACK IN TIME (0 = today)
current_date = datetime.now() - timedelta(days = delta)

'''
BENCHMARK INDEX
- Set benchmark using ticker benchmark_ticker from above: gather history
- Calculate applicable indicators 
- Add rolling cols (means, mins, maxes, z_scores)
- change column names to denote vs. stock column names
'''
##Indicators
benchmark_history = yf.Ticker(benchmark_ticker).history(period = period)
benchmark_history = ra.add_all_features(benchmark_history, cols, drop_cols, periods, funcs)
##Denote market benchmark column names
benchmark_history.columns = [f'market_{col}' for col in benchmark_history.columns]

'''
MAIN LOOP
- for each stock in watchlist, initialize asset 
- then add indicators and rolling col aggregates
- JOIN: Benchmark history info based on Date
- Calculate growth % deltas for all figures; column concatenate with original figures in 'cols' list
- Drop all null columns and any null rows, rearrange columns 
'''
features = pd.DataFrame()
for ticker in WATCHLIST.index: 
    # Initialize asset history
    try:
        asset = yf.Ticker(ticker)
        asset_figs = asset.history(period = period)
    except Exception as err:
        print(str(err))
        continue

    # Add Rolling columns + indicators
    asset_figs = ra.add_all_features(asset_figs, cols, drop_cols, periods, funcs)
    # JOIN: Benchmark info
    asset_figs = pd.merge(asset_figs, benchmark_history, on = 'Date')

    # Calculate growth rates, concat with original figs and ticker info
    deltas = asset_figs.diff()/asset_figs.shift(1)
    deltas.columns = [f'{col}_delta' for col in deltas.columns]

    asset_figs = pd.concat([asset_figs[cols],
                            asset_figs.iloc[:, ['z_score' in col for col in asset_figs.columns]],
                            deltas], 
                            axis = 1)
    # Set sector + Ticker cols
    try: 
        asset_figs['sector'] = asset.info['sector']
    except: 
        asset_figs['sector'] = 'No Sector'
    asset_figs['Ticker'] = ticker
    
    asset_figs.reset_index(inplace = True)
    asset_figs = asset_figs.loc[:, features_to_keep[0]]

    features = features.append(asset_figs.iloc[-(delta+1),:])
    print(ticker); print(features.shape)

first_cols = ['Date','sector', 'Ticker']; rem_cols = [col for col in features.columns if col not in first_cols]
features = features[first_cols+rem_cols]
features.reset_index(drop = True, inplace = True)
features.to_csv(f'ml/regression/lm_inputs/inputs/input_features_{current_date.strftime("%m-%d-%Y")}.csv')