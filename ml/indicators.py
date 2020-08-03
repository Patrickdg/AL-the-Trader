# LIBRARIES
import pandas as pd 
import numpy as np

# INDICATOR FUNCTIONS
##MOMENTUM INDICATORS
###RSI
def calc_rsi(df, period = ''):
    # If no period  passed; used for rolling apply func
    period = len(df) if period == '' else period

    # RS 
    df = pd.Series(df)
    delta = df.diff()
    
    u_changes = delta[delta > 0]
    d_changes = delta[delta < 0].map(abs)

    try: 
        u_avg = sum(u_changes)/period
        d_avg = sum(d_changes)/period
        rs = u_avg / d_avg

        #RSI
        rsi = 100 - (100/(1+rs))
    except ZeroDivisionError as err:
        print(str(error))
        rsi = 100
    return rsi

##TREND INDICATORS 
###MACD
def calc_macd(data, params = [12, 26, 9]):
    data = pd.Series(data)
    period_fast = params[0]
    period_slow = params[1]
    signal = params[2]

    fast_ema = data.ewm(span = period_fast, 
                        min_periods = period_fast, 
                        adjust = False).mean()
    slow_ema = data.ewm(span = period_slow, 
                        min_periods = period_slow, 
                        adjust = False).mean()
    macd = fast_ema - slow_ema

    signal_line = macd.ewm(span = signal, adjust = False).mean()
    hist = macd - signal_line
    hist = hist.rename('macd_hist')

    return hist, hist.shift(1) 

##VOLATILITY INDICATORS
###BOLLINGER BANDS
def calc_bb(data, params): 
    data = data.sort_index()
    deviations = params['a']
    trend_period = params['b']
    
    df = pd.DataFrame(data.rename('price'))

    df['trend'] = data.rolling(window = trend_period).mean()
    df['std'] = df['price'].rolling(window = trend_period).std()
    margin = df['std'] * deviations
    df['upper_band'] = df['trend'] + margin
    df['lower_band'] = df['trend'] - margin

    # Buy/sell indicator: 
    df['bb_bs'] = np.where(df['price'] <= df['lower_band'], 'buy', 
                    np.where(df['price'] >= df['upper_band'], 'sell',
                        'hold'))

    return df['bb_bs']

def add_indicators(df, cols, periods, inds): 
    pass
