import pandas as pd
import numpy as np

# Rolling aggregates
def rolling_mean(df, col_name, period):
    rolling = df[col_name].rolling(period).mean()
    return rolling

def rolling_max(df, col_name, period):
    rolling = df[col_name].rolling(period).max()
    return rolling

def rolling_min(df, col_name, period):
    rolling = df[col_name].rolling(period).min()
    return rolling

def rolling_stdev(df, col_name, period):
    rolling = df[col_name].rolling(period).std()
    return rolling

def z_score(df, col_name, period):
    x_bar = rolling_mean(df, col_name, period)
    stdev = rolling_stdev(df, col_name, period)
    rolling = (df[col_name] - x_bar)/stdev
    return rolling

def add_rolling_cols(df, cols, periods, funcs): 
    for col in cols:
        for n in periods: 
            for func in funcs:
                agg_name = func.__name__
                df[f'{col}_{agg_name}_{n}'] = func(df, col, n)
    return df

if __name__ == '__main__': 
    import yfinance as yf
    import ml.indicators as ind
    import time

    watchlist = pd.read_excel('ml/watchlist_ml.xlsx', sheet_name = 'watchlist')
    period = '3y' # for individual stock history
    cols = ['Open','High','Low','Close','Volume', 'rsi', 'macd_hist', 'bb_upper_band', 'bb_upper_diff', 'bb_lower_band', 'bb_lower_diff']
    drop_cols = ['Dividends', 'Stock Splits']
    periods = [5, 10, 21, 130] # for rolling aggregate calcs
    funcs = [rolling_mean, rolling_max, rolling_min, rolling_stdev, z_score]

    benchmark_ticker = 'VTSMX' # The Vanguard Total Stock Market Index 
    ##Indicators
    benchmark_history = yf.Ticker(benchmark_ticker).history(period = period)
    start = time.time()
    benchmark_history['rsi'] = benchmark_history['Close'].rolling(15).apply(ind.calc_rsi) 
    benchmark_history['macd_hist'] = ind.calc_macd(benchmark_history['Close']) 
    benchmark_history['bb_upper_band'], benchmark_history['bb_upper_diff'], benchmark_history['bb_lower_band'], benchmark_history['bb_lower_diff'] = ind.calc_bb(benchmark_history['Close'])
    end = time.time()
    ##Rolling Aggregates 
    benchmark_history = add_rolling_cols(benchmark_history, cols, periods, funcs).drop(drop_cols, axis = 1)
    ##Denote market benchmark column names
    benchmark_history.columns = [f'market_{col}' for col in benchmark_history.columns]

    print(benchmark_history)
    print(end - start)