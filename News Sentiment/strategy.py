# -*- coding: utf-8 -*-
"""
Created on Sun Jan  1 18:17:13 2023

@author: leocb
"""

# =============================================================================
# LIBRARIES
# =============================================================================

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

# =============================================================================
# CONSTANTS
# =============================================================================

TRADE_SIZE = 10000
RISK_FREE_INTEREST_RATE = 0.02
COMMISSION = 0.0005

# =============================================================================
# FUNCTIONS/CLASSES
# =============================================================================

def print_na(df):
    # Print the number of null values in each column
    null_counts = df.isna().sum()
    
    # Filter to show only columns with null values
    null_counts = null_counts[null_counts > 0]
    print(null_counts)

def get_sharpe_ratio(returns, annualized_risk_free_rate):
    # The Sharpe ratio is the average return earned in excess of the risk-free rate per unit of volatility
    # or total risk. Volatility is a measure of the dispersion of returns

    daily_returns = np.mean(returns)
    vol = np.std(returns)
    
    if vol > 0:
        sharpe_ratio = ((1+daily_returns)**252-1 - annualized_risk_free_rate) / (vol*np.sqrt(252))
    else:
        return 0
    
    return sharpe_ratio

def max_drawdown(returns):
  # Calculate the cumulative returns
  cum_returns = [1.0]
  for r in returns:
    cum_returns.append(cum_returns[-1] * (1 + r))

  # Calculate the maximum drawdown
  max_drawdown = 0
  for i in range(len(cum_returns)):
    max_drawdown = min(max_drawdown, cum_returns[i] - max(cum_returns[:i+1]))
  
  # Return the maximum drawdown
  return max_drawdown

# =============================================================================
# 
# =============================================================================
# =============================================================================
# MAIN
# =============================================================================
# =============================================================================
# 
# =============================================================================

if __name__ != "__main__":
    exit
    
df = pd.read_parquet(r".\data.parquet")

df = df.loc[df['Symbol'].isin(symbols_trade)].copy()

print(min(df.index), " ", max(df.index))

# added lagged close
df['Adj Close_1'] = df.groupby('Symbol')['Adj Close'].shift()
df['Adj Close_fut'] = df.groupby('Symbol')['Adj Close'].shift(-1)

df_grouped = df.groupby(by="Symbol")

mat_pl = list()
sharpe_ratios = list()
daily_returns = list()
symbols = []
n_trades = 0

for group_name, df_group in df_grouped:
    symbols.append(group_name)
    
    is_long_trade_open = False

    long_open_prices = list()
    long_close_prices = list()
    
    long_returns = list()
    
    for row_index, row in df_group.iterrows():
        
        # long trade
        if is_long_trade_open:
            # register daily return
            if row["Adj Close"] > 0:
                long_returns.append(((1-COMMISSION)*row["Adj Close_fut"]/row["Adj Close"])-1)
            else:
                long_returns.append(0)
            
            # close trade
            if row["News - Negative Sentiment"] > 0:
                is_long_trade_open = False
                long_close_prices.append(row["Adj Close_fut"])
        else:
            # register daily return
            long_returns.append(0)
            
            # open trade
            if row["News - Positive Sentiment"] > 0:
                is_long_trade_open = True
                long_open_prices.append(row["Adj Close_fut"])
                n_trades += 1
                    
    if len(long_close_prices) != len(long_open_prices):
        del long_open_prices[-1]
        
    sharpe_ratios.append(get_sharpe_ratio(long_returns,RISK_FREE_INTEREST_RATE))
    daily_returns.append(long_returns)

    # calculate pl
    long_pl = 0

    for i in range(len(long_open_prices)):
        long_pl += TRADE_SIZE*(long_close_prices[i]/long_open_prices[i]-1)
        
    mat_pl.append([group_name,long_pl])

df_pl = pd.DataFrame(data=mat_pl,columns=["symbol","pl"])

df_pl["pl"].sum()
df_pl["pl"].mean()
df_pl["pl"].median()
df_pl["pl"].std()
sum(df_pl["pl"] > 0)

df_dailyreturns = pd.DataFrame(np.transpose(daily_returns),columns=symbols)
dailyreturns_mean = df_dailyreturns.mean(axis=1)

np.cumsum(dailyreturns_mean)

get_sharpe_ratio(list(dailyreturns_mean),RISK_FREE_INTEREST_RATE)
max_drawdown(dailyreturns_mean)

sp = pd.read_clipboard()
sp = sp.replace(",",".", regex=True)
sp.columns = ["return"]
sp["return"] = sp["return"].astype(float)

get_sharpe_ratio(list(sp["return"]),RISK_FREE_INTEREST_RATE)

max_drawdown(list(sp["return"]))

# =============================================================================
# PORTFOLIO CREATIOIN
# =============================================================================
import yfinance as yf
from sklearn.decomposition import SparsePCA
import seaborn as sns

symbols = list(df["Symbol"].unique())
s = ""

for symbol in symbols:
    s += symbol + " "

s.rstrip()

start_date = '2010-01-01'
end_date = '2020-01-01'
 
# Add multiple space separated tickers here
data = yf.download(s, start_date, end_date)

data["Date"] = data.index
 
data = data[["Date", "Open", "High","Low", "Close", "Adj Close", "Volume"]]
 
data.reset_index(drop=True, inplace=True)

# get downloaded symbols
symbols_dl = list()

for i in range(len(data.columns)):
    symbols_dl.append(data.columns[i][1])
    
symbols_dl = list(set(symbols_dl))

del symbols_dl[0]

# get columns for data matrix
cols = list()
for symbol in symbols_dl:
    cols.append(("Adj Close",symbol))

data_closes = data[cols].copy()

data_closes = data_closes.dropna(axis=1,how="any")
print_na(data_closes)

# normalize
norm_data =(data_closes-data_closes.mean())/data_closes.std()
norm_data.values.shape

pca = SparsePCA(n_components=50)
pca.fit_transform(norm_data)

SparsePCA(norm_data.values)

components = pca.components_
df_components = pd.DataFrame(components, columns=norm_data.columns)
sns.heatmap(df_components, cmap='RdYlBu')

# Create a list to store the variables and correlation values for each component
variables_by_component = []

# Iterate over the components
for component in components:
    # Get the index of the most correlated variable
    top_variable = component.argmax()
    
    # Get the name of the variable
    variable_name = norm_data.columns[top_variable]
    
    # Get the correlation value
    correlation = component[top_variable]
    
    # Add the variable and correlation value to the list
    variables_by_component.append((variable_name, correlation))

# Print the list of variables and correlation values
print(variables_by_component)

# get symbols only
symbols_trade = list()

for i in range(len(variables_by_component)):
    symbols_trade.append(variables_by_component[i][0][1])
    
symbols_trade = list(set(symbols_trade))