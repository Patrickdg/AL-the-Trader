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