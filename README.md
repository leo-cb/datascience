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

## Genetic Algorithms (R)

A genetic algorithm with elitism and mutations developed from scratch in R in order to solve a least cost path optimization problem. Non-admissible solutions are penalized through a carefully constructed objective function, which also ensures that the algorithm scales well with the problem's dimension. Additionally, it creates performance charts for different hyperparameter values to allow for the selection of proper hyperparameters.

## OriginsRO market (Python)

Scrapes data from an online game's market data using BeautifulSoup to find and alert about undervalued items.
