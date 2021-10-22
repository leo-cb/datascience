# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 02:49:57 2018

@author: Leonardo
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from functions import getStocksData,Fundamentals,FindSupport,FindResistance
from datetime import datetime
import random
import matplotlib.pyplot as plt

# =============================================================================
# functions
# =============================================================================

def nearest(items, pivot):
    """Returns the datetime in items which is the closest to the date pivot"""
    return min(items, key=lambda x: abs(x - pivot))

def getPerctGrowth(timeseries):
    """timeseries is a dict with format {year:value}. Ignores different signs
    comparisons and returns a dict with the growth percentages"""
    
    # get years, excluding the last one, as list
    indexYears = list(timeseries.keys())
    del indexYears[-1]
    
    growth = dict()
    for y in indexYears:
        # only compare values with the same sign
        if timeseries[y-1]*timeseries[y] > 0:
            growth[y]=(timeseries[y]-timeseries[y-1])/abs(timeseries[y-1])
    
    return growth

def getPriceNearDate(df,price,date):
    """Get price nearest to the date given, from ticker's dataframe df"""
    
    # get prices and dates
    prices = df[price]
    dates = df.index.values
    
    # get bar open dates as list of datetime vars
    openTimes = list()
    for timestamp in dates.tolist():
        ts = timestamp*10**-9
        openTimes.append(datetime.fromtimestamp(ts).replace(hour=0,minute=0))
                
    # get nearest date
    nearestDate = nearest(openTimes,date)
    
    # return price of nearest date to 'date'
    return prices[nearestDate]

# =============================================================================
# constants
# =============================================================================
    
YEARS = 5 # total number of years of available data
BENCHMARK_TICKER = "IXIC" # benchmark index ticker
STOCKS_SELECT_NUMBER = 100 # number of stocks to select from list

# =============================================================================
# beginning of script
# =============================================================================

# read stocks from file
file = pd.read_table("nasdaqlisted.txt","|")
stocksList = file["Symbol"].tolist()

# randomly choose some stocks
size = len(stocksList)
indices = random.sample(range(0,size),STOCKS_SELECT_NUMBER)

newStocks = list()
for i in indices:
    newStocks.append(stocksList[i])
    
# refresh original list
stocksList = newStocks.copy()

# get stocks data in dict of dataframes
stocks = getStocksData(stocksList)

# get benchmark data
benchmark = getStocksData([BENCHMARK_TICKER])[BENCHMARK_TICKER]

# get current year
yearNow = datetime.now().year

# prepare data matrix for 4 variables
dataMatrix = np.zeros((1,4))

# =============================================================================
# iterate through each loaded stock
# =============================================================================

for stock,df in stocks.items():
    
# =============================================================================
#     get base fundamentals
# =============================================================================
    
    # intialize classes for this stock
    income = Fundamentals(stock,"income-statement")
    balance = Fundamentals(stock,"balance-sheet")
            
    # get net income value
    netIncome = income.getValues("Net Income")
    
    # get total assets
    totalAssets = balance.getValues("Total Assets")
    if 0 in totalAssets.values():
        continue
    
    # try to find total cash value
    totalCash = balance.getValues("Cash &amp; Short Term Investments")
    if len(totalCash) == 0:
        totalCash = balance.getValues("Total Cash &amp; Due from Banks")
    
    # unable to find total cash
    if len(totalCash) == 0:
        print("Unable to find equivalent of total cash for stock " + stock)
        continue
    
# =============================================================================
#     get fundamentals growth
# =============================================================================
    
    # get net income growth %
    growthNetIncome = getPerctGrowth(netIncome)
    
    if len(growthNetIncome) == 0:
        continue
    
    # get 'assets = total assets - total cash' dictionary
    assets = dict()
    for key in totalCash.keys():
        assets[key] = totalAssets[key]-totalCash[key]
        
    # get assets growth %
    growthAssets = getPerctGrowth(assets)
    
    if len(growthAssets) == 0:
        continue

    # get dates for stocks and benchmark dataframes
    dates = benchmark.index.values
    
    # get years from highest to lowest, excluding the last one, as list
    indexYears = list(assets.keys())
    del indexYears[-1]
    
    # update years index list by removing years where there weren't comparisons
    # in either income or assets growth
    indicesToDel = list()
    for i,y in enumerate(indexYears):
        if y not in growthNetIncome.keys() or y not in growthAssets.keys():
            indicesToDel.append(i)

    for i in sorted(indicesToDel,reverse=True):
        del indexYears[i]
# =============================================================================
#     get prices growth
# =============================================================================
        
    # get benchmark growth %
    growthBenchmark = dict()
    
    for y in indexYears:
        currentClose = getPriceNearDate(benchmark,"Close",
                         datetime(y,12,31))
        previousClose = getPriceNearDate(benchmark,"Close",
                         datetime(y-1,12,31))
        
        if previousClose != 0:
            growthBenchmark[y] = (currentClose-previousClose)/previousClose
        else:
            break
    
    if previousClose == 0:
        continue
    
    # get stock growth %
    growthStock = dict()
    
    for y in indexYears:
        currentClose = getPriceNearDate(df,"Close",datetime(y,12,31))
        previousClose = getPriceNearDate(df,"Close",datetime(y-1,12,31))
        
        if previousClose != 0:
            growthStock[y] = (currentClose-previousClose)/previousClose    
        else:
            break
    
    if previousClose == 0:
        break
    
    # make lists out of growth dicts
    growthStockL = list(); growthNetIncomeL = list(); growthAssetsL = list()
    growthBenchmarkL = list()
    
    for y in indexYears:
        growthStockL.append(growthStock[y])
        growthNetIncomeL.append(growthNetIncome[y])
        growthAssetsL.append(growthAssets[y])
        growthBenchmarkL.append(growthBenchmark[y])
        
    # add to the inputs and targets matrix
    stockData = np.column_stack((growthStockL,growthNetIncomeL,growthAssetsL,growthBenchmarkL))
    dataMatrix = np.concatenate((dataMatrix,stockData))

# delete data's first dummy row
dataMatrix = np.delete(dataMatrix,(0),axis=0)

# =============================================================================
# multiple linear regression
# =============================================================================

dataDf = pd.DataFrame(columns=["Stock","NetIncome","Assets","Benchmark"],data=dataMatrix)
mlr = sm.ols(formula="Stock~Benchmark",data=dataDf).fit()
print(mlr.summary())

#dataDf = pd.DataFrame(columns=["Stock","NetIncome","Assets","Benchmark"],data=dataMatrix)
#mlr = sm.ols(formula="Stock~Benchmark",data=dataDf).fit()
#print(mlr.summary())