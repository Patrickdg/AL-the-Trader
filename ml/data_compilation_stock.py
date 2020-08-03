'''
For each stock in watchlist, gather stock price + volume data + rolling aggregates
'''

#LIBRARIES
import pandas as pd
import numpy as np
import yfinance as yf
import ml.rolling_agg_funcs as ra
import ml.indicators as ind

import imp
imp.reload(ra)
imp.reload(ind)

#DECLARATIONS/PARAMS
watchlist = pd.read_excel('ml/watchlist_ml.xlsx', sheet_name = 'watchlist')
period = '5y' # for individual stock history
cols = ['Open','High','Low','Close','Volume', 'rsi', 'macd_hist', 'bb_upper_band', 'bb_upper_diff', 'bb_lower_band', 'bb_lower_diff']
drop_cols = ['Dividends', 'Stock Splits']
periods = [5, 10, 15, 21, 130] # for rolling aggregate calcs
funcs = [ra.rolling_mean, ra.rolling_max, ra.rolling_min, ra.rolling_stdev, ra.z_score]
benchmark_ticker = 'VTSMX' # The Vanguard Total Stock Market Index 

#SET BENCHMARK INDEX, add indicators + rolling aggregates
benchmark_history = yf.Ticker(benchmark_ticker).history(period = period)

benchmark_history['rsi'] = benchmark_history['Close'].rolling(15).apply(ind.calc_rsi) #RSI
benchmark_history['macd_hist'] = ind.calc_macd(benchmark_history['Close']) #MACD
benchmark_history['bb_upper_band'], benchmark_history['bb_upper_diff'], benchmark_history['bb_lower_band'], benchmark_history['bb_lower_diff'] = ind.calc_bb(benchmark_history['Close'])# BBs
benchmark_history = ra.add_rolling_cols(benchmark_history, cols, periods, funcs).drop(drop_cols, axis = 1)

benchmark_history.columns = [f'market_{col}' for col in benchmark_history.columns]

# MAIN LOOP
for ticker in watchlist.ticker: 
    # Initialize asset history
    asset = yf.Ticker(ticker)
    asset_figs = asset.history(period = period)

    # Add Rolling columns + indicators
    asset_figs['rsi'] = asset_figs['Close'].rolling(15).apply(ind.calc_rsi) #RSI
    asset_figs['macd_hist'] = ind.calc_macd(asset_figs['Close']) #MACD
    asset_figs['bb_upper_band'], asset_figs['bb_upper_diff'], asset_figs['bb_lower_band'], asset_figs['bb_lower_diff'] = ind.calc_bb(asset_figs['Close'])# BBs

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
    
    print(ticker); print(asset_figs.shape)
    
    # Drop all-Nan columns, Reorder columns
    asset_figs.dropna(how = 'all', axis = 1, inplace = True)
    asset_figs.dropna(how = 'any', axis = 0, inplace = True)
    asset_figs.reset_index(inplace = True)

    first_cols = ['Date','sector']; rem_cols = [col for col in asset_figs.columns if col not in first_cols]
    asset_figs = asset_figs[first_cols+rem_cols]
    
    asset_figs.to_excel(f'ml/stock_data/{ticker}.xlsx')
