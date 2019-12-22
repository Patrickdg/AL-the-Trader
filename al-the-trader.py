#==============================
# Resources

## Finviz
### https://github.com/mariostoev/finviz

## yFinance
### https://pypi.org/project/yfinance/



#==============================
# Libraries
import finviz
from finviz.screener import Screener
from finviz.portfolio import Portfolio
import pandas as pd

import yfinance as yf

#==============================

# Individual Stocks
aapl = finviz.get_stock('AAPL')
aapl.keys()



hist = yf.Ticker('MSFT')
hist.history(period = "max")
hist.calendar


