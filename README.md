# AL-the-Trader

## Description 
Automated stock paper-trading algorithm using daily triggers to simulate buy/sell transactions on specified watchlist. **Only intended for simulation and demonstration purposes, NOT for live trading.**

Current version tracks the 30 stocks in the DOW (as of May 1, 2020).

###**[Live Dashboard - Portfolio Summary](https://public.tableau.com/profile/patrick.de.guzman5555#!/vizhome/ALtheTrader-PortfolioSummary/Dashboard1)**

## Domains 
- Python (scraping, triggers, & transactions)
    - pandas (wrangling), yfinance (scraping)
- Excel (portfolio tracking)
- Tableau (portfolio visualization & additional analytics)

## Planned Implementations 
- Automatic watchlist updates (based on trending indicators + other screens)
- Optimal (+ automatic) technical indicator selection per watchlist stock via back-testing, comparison of returns, statistical significance testing
    - Discounted Cash Flow (DCF) Valuation modelling triggers
    - Dynamic algorithm strategy (bear/bull market triggers, MACD/SMA/RSI threshold adjustments)
- Sentiment analysis (news, twitter)
- Short/margin trading
- Analyst recommendations
- Backtesting