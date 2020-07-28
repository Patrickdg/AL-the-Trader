# AL-the-Trader

## Description 
Automated algorithmic stock paper-trading using daily triggers to simulate buy/sell transactions on specified watchlist. **Only intended for simulation and demonstration purposes, NOT for live trading.**  

Algorithm currently uses RSI (30, 70) bounds as (buy, sell) triggers for simplicity.  
Upcoming integrations will include DCF valuations, 50-200SMA, Bollinger bands, and MACD indicators.

Current watchlist tracks the 30 stocks in the DOW (as of May 1, 2020).

Scraping is performed using *yfinance* module and *pandas* to wrangle data into excel. 

**[Live Dashboard - Portfolio Summary](https://public.tableau.com/profile/patrick.de.guzman5555#!/vizhome/ALtheTrader-PortfolioSummary/Dashboard1)**

## Domains 
- Python (scraping, triggers, & transactions)
    - pandas (wrangling), yfinance (scraping)
- Excel (portfolio tracking)
- Tableau (portfolio visualization & additional analytics)

## In-progress Implementations
- Additional technical indicators: 
    - DCF  
    - 50-200SMA  
    - Bollinger bands  
    - MACD  
- Portfolio tracking & Dashboard updates: daily/weekly/monthly performance measures  
- Dynamic algorithms

## Future Implementations 
- Dynamic watchlist (based on trending indicators + other screens)
- Optimal (+ automatic) technical indicator selection per watchlist stock via back-testing, comparison of returns, statistical significance testing
    - Discounted Cash Flow (DCF) Valuation modelling triggers
    - Dynamic algorithm strategy (bear/bull market triggers, MACD/SMA/RSI threshold adjustments)
- Sentiment analysis (news, twitter)
- Short/margin trading
- Analyst recommendations
- Backtesting
