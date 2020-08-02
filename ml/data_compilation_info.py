'''
For each stock in watchlist, gather yfinance info
'''

#LIBRARIES
import pandas as pd
import numpy as np
import yfinance as yf

#DECLARATIONS
watchlist = pd.read_excel('ml/watchlist_ml.xlsx', sheet_name = 'watchlist')

relevant_info_columns = ['52WeekChange', 'averageDailyVolume10Day', 'averageVolume', 'averageVolume10days', 'beta', 'bookValue', 'dayHigh', 'dayLow', 'dividendRate', 'dividendYield', 'earningsQuarterlyGrowth', 'enterpriseToEbitda', 'enterpriseToRevenue', 'enterpriseValue', 'fiftyDayAverage', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'fiveYearAvgDividendYield', 'floatShares', 'forwardEps', 'forwardPE', 'fullTimeEmployees', 'heldPercentInsiders', 'heldPercentInstitutions', 'industry', 'marketCap', 'netIncomeToCommon', 'open', 'payoutRatio', 'pegRatio', 'previousClose', 'priceToBook', 'priceToSalesTrailing12Months', 'profitMargins', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketOpen', 'regularMarketPreviousClose', 'regularMarketPrice', 'regularMarketVolume', 'sector', 'sharesOutstanding', 'sharesPercentSharesOut', 'sharesShort', 'sharesShortPriorMonth', 'shortPercentOfFloat', 'shortRatio', 'symbol', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'trailingEps', 'trailingPE', 'twoHundredDayAverage', 'volume']

assets = pd.DataFrame()
for ticker in watchlist.ticker: 
    # Initialize asset info
    asset = yf.Ticker(ticker)
    asset_info = asset.info
    asset_df = pd.DataFrame(asset_info.items()).set_index([0]).transpose()

    print(ticker)
    assets = pd.concat([assets, asset_df]); print(assets.shape)
    
# Replace all 'None' values with Nan, then drop cols with all NaNs
assets = assets.replace('None', np.nan).dropna(axis = 1, how = 'all')
assets = assets[relevant_info_columns]
assets.to_excel('ml/consolidated_asset_info.xlsx')