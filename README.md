## Stocks scraping (Python)

<p>Scrapes stocks' balance sheet, income statement, cash flow data and other information such as company's description and industry, from any public company listed in wsj.com. Collects price and volume data through the AlphaVantage API.</p>
<p><b>functions.py</b> - library file to scrape data from wsj.com and AlphaVantage API.</p>
<p><b>valuationModel.py</b> - creates a regression with net income and assets as predictors of stock growth (compared to the benchmark index NASDAQ).</p>
<p><b>save_financials.py</b> - creates a list of financial indicators such as revenue growth, long-term debt to equity, interest to EBIT, liquidity ratios and saves the data into a dataframe.</p>

## Options trading (Python)

Estimates the return on investment of a given option, based on the underlying asset's historical prices, using the option's current market price, strike, premium, expiry date, whether it's a call or put and whether it's an American or European style option.
This is performed through a bootstrapping approach, so that no assumptions on the prices' variation distribution need to be made. 
The return on investment of all the tested options was negative, some reaching nearly a -100% ROI. The conclusion of these simulations is that most options of European and American stocks are severely overvalued given the underlying price variation, which favors selling options rather than buying as a trading strategy. However, selling options involves the potential of heavy losses (exposure to 'black swan' events), so a proper risk mitigation strategy is highly advised.
Two main improvements can be made:
<ol>
  <li>A backtester to test the strategy with historical options data.</li>
<li>Estimate a theoretical distribution for the underlying asset's price variation based on the historical data (such as Wald distribution). This approach could make the simulation more sensitive to extreme, non-observed variations in price that may significantly impact an option's return on investment.</li>
  </ol>
  
## News Sentiment (Python)

This trading system uses a dataset that is created from the sentiment analysis of news headlines for the Fortune 500 stocks (https://www.kaggle.com/datasets/parsabg/stocknewseventssentiment-snes-10). This dataset was retrieved from Aylien's news API. The dataset has two key metrics: the positive daily news sentiment, and the negative daily news sentiment. Each one of these may have a value of 0 or a positive number. It may be the case, for example, that both positive and negative sentiment show a positive value, which would mean there were both positive and negative news during that specific day.

The OHLC data for each stock and S&P500 were obtained from Yahoo Finance.

I created the strategy, along with a basic backtesting system and functions to retrieve the strategy's basic metrics on Python, using the pandas and scikit-learn libraries.

<strong>Trading algorithm:</strong>
When the positive sentiment > 0, enter a long trade on the closing price of the next day
Close the trade when the negative sentiment > 0

<strong>Portfolio selection:</strong>
A portfolio that attempts to minimize the variance (e.g. choose a set of uncorrelated Fortune 500 stocks) is created by a sparse PCA: for an universe of 500 stocks, the first 50 components are obtained, and the stocks chosen for the portfolio are the ones who correlate the most with each one of these components. Since the components are approximately uncorrelated to each other, the chosen stocks are also expected to be the least correlated to each other as possible, therefore creating a minimum variance portfolio with a non-parametric method. The final included number of stocks in the portfolio were 42, as some stocks correlated the most with more than one component.

The date range for this analysis was from 2010-01-01 to 2020-01-01 (no time overlap with the backtesting data).

<strong>Results</strong> (2020-09-30 to 2022-06-30):

The aforementioned sentiment data was available from 2020-09-30 to 2022-06-30 (21 months), which limited the backtesting period. For this reason, although the obtained results were promising (a quite high Sharpe ratio compared to the benchmark, low maximum drawdown), it would be necessary to obtain more sentiment data to test the algorithm on a larger timeframe.

<strong>Strategy:</strong>

ROI: 35.14%
Sharpe ratio (2% risk-free i.r.): 1.69
Maximum drawdown: -11.5%
Average ROI per stock: 36.79%
Std ROI per stock: 46.25%
Median ROI per stock: 18.68%
Winning stocks (profit > 0): 61.9%

Benchmark (S&P 500)
ROI S&P: 12%
Sharpe ratio S&P (2% risk-free i.r.): 0.378
Maximum drawdown: -24.3%

If more data was available (ideally, including a steep downturn period), in order to further improve the system, another algorithm/implementation for the creation of the minimum variance portfolio could be tried, and other rules having to do with sentiment could also be tested.

## Genetic Algorithms (R)

A genetic algorithm with elitism and mutations developed from scratch in R in order to solve a least cost path optimization problem. Non-admissible solutions are penalized through a carefully constructed objective function, which also ensures that the algorithm scales well with the problem's dimension. Additionally, it creates performance charts for different hyperparameter values to allow for the selection of proper hyperparameters.

## Synthetic stocks (R)

Synthetic stock time-series have diverse uses, such as valuing financial options to backtesting strategies. This script creates a synthetic price time-series, based on historical prices of a given stock, by first fitting a gjrGARCH model and then using this model to simulate prices.

**simulate_stock_garch_development.R** - fits a gjrGARCH(0,0)(1,1) with normal error distribution to "GOOGL" close prices log differences from Jan2010 to June2022. gjrGARCH was chosen as non-symmetric innovations are often observed in financial time-series. However, Pearson's goodness-of-fit rejected normality. Therefore, a gjrGARCH(0,0)(1,1) was fitted with t-student error distribution. Pearson's goodness-of-fit did not reject the assumed distribution and the residuals did not exhibit auto-correlation. Every parameter except for alpha1 (p-value approx. 0.2) showed a p-value < 0.01. A noteworthy observation is that negative returns impact on volatility was significantly higher than the positive returns', as seen by the "News impact curve". This model was chosen for production.

**simulate_stock_garch_production.R** - Fits a gjrGARCH(0,0)(1,1) to the chosen ticker's ("GOOGL" by default) close prices log differences and outputs synthetic close prices time-series.

## Dow Jones Best Stock (Python)

Predicts the best performing stock of Dow Jones index on the following week, based on the previous week price and volume data. Some features such as traded volume (price * volume), performance ranking, volume growth ranking are created. As it is an heavily imbalanced dataset, SMOTE algorithm was used to created a balanced dataset and XGBoost was used to perform binary classification, followed by hyperparameter optimization of two hyperparameters. Obtained a precision of 48%, recall of 50% and AUC of 0.7 on the test dataset.

## OriginsRO market (Python)

Scrapes data from an online game's market data using BeautifulSoup, and compares the value with similar items and historical averages to alert about undervalued items.


