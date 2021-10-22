# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 21:56:31 2020

@author: Leonardo
"""

# issue: ROI and percent win are very similar for every barrier value. Percent win should be much higher for barriers close to 0 than higher ones.
# issue: ROi function depends on global variables
# improvement: make it easier to simulate multiple options from different assets

# =============================================================================
# IMPORTS
# =============================================================================

from math import log,exp,floor
import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dt
import random
from statsmodels.distributions.empirical_distribution import ECDF
import matplotlib.pyplot as plt

# =============================================================================
# MACROS
# =============================================================================

# % change from baseline
BARRIERS = [0.01,1]

# define parameters
time_window_in_days = 1000 # period to gather variations
time_offset_each_iter_in_days = 90 # each iteration decreases this number of days in the end date
time_offset_max_in_days =  1000 # the minimum end date goes back this number of days

# =============================================================================
# FUNCTIONS
# =============================================================================

def PerctChange(initial,final):
    return (final-initial)/abs(initial)

def GetProportion(lst,positive=True):
    if len(lst) == 0:
        return 0
    
    if positive:
        return sum([1 for x in lst if x > 0])/len(lst)
    else:
        return sum([1 for x in lst if x < 0])/len(lst)
    
def CreateBarriers(option):
    """ Create price barriers based on multipliers vector """
    barriers = np.array(BARRIERS)
    
    if option["is_call"]:
        return (1 + barriers) * option["strike"]
    else:
        return (1 - barriers) * option["strike"]
    
def GetVariationsFromBarrier(data,strike,barrier,days_offset):
    """ Gets variations above or below barrier (0 if barrier is not broken).
    Barrier is defined as % change from base price."""
    
    # get values
    data_val = data.values
    
    # is upper barrier
    is_upper = barrier >= 0
    
    # calculate percentage variations between pairs of pre-defined dates
    var = [np.NaN]*len(data_val)
    days = [np.NaN]*len(data_val)
    date_base = [np.NaN]*len(data_val)
    
    # j is the origin (older) shift
    for j in range(len(data_val)-1,0,-1):
        
        # k is the current (newer) shift
        for k in range(j-1,0,-1):
            
            # difference in days from j to k
            days_diff = (data_val[k,7]-data_val[j,7]).days
            
            # variation from j
            var_base = PerctChange(data_val[j,1],data_val[k,1])
            
            # upper barrier
            if is_upper:
                if (days_diff < days_offset and data_val[k,1] >= strike*(1+barrier)) or\
                days_diff == days_offset:
                    var[j] = var_base
                    days[j] = days_diff
                    date_base[j] = data_val[j,7]
                    break
                elif days_diff > days_offset:
                    var[j] = PerctChange(data_val[j,1],data_val[k+1,1])
                    days[j] = (data_val[k+1,7]-data_val[j,7]).days
                    date_base[j] = data_val[j,7]
                    break
                
            # lower barrier
            else:
                if (days_diff < days_offset and data_val[k,1] <= strike*(1+barrier)) or\
                days_diff == days_offset:
                    var[j] = var_base
                    days[j] = days_diff
                    date_base[j] = data_val[j,7]
                    break
                elif days_diff > days_offset:
                    var[j] = PerctChange(data_val[j,1],data_val[k+1,1])
                    days[j] = (data_val[k+1,7]-data_val[j,7]).days
                    date_base[j] = data_val[j,7]
                    break

    return var, days, date_base

def SimulateOptionProfitLoss(current_price, option, var, n_trades, n_simulations):
    """Simulates PL and percentiles for n_trades in n_simulations, for a given 
    current_price, option and variation list var."""
  
    sum_pl = [0]*n_simulations
    pl_all = [0]*n_simulations*n_trades
    
    # loop through each simulation
    for k in range(n_simulations):
        
        # drop nan's from var
        var = [x for x in var if ~np.isnan(x)]
    
        # create bootstrap variations
        var_bootstrap = random.choices(var, k=n_trades)
        
        # initialize pl as empty list
        pl = [np.NaN]*n_trades
        
        # loop through each trade
        for i in range(n_trades):
            if option["is_call"]:
                pl[i] = max((1+var_bootstrap[i])*current_price - option["strike"],0) - option["premium"]
            else:
                pl[i] = max(option["strike"] - (1+var_bootstrap[i])*current_price,0) - option["premium"]
                
            pl_all[n_trades*k + i] = pl[i]

        # calculate PL for current simulation        
        sum_pl[k] += sum(pl)
      
#    premium_total = n_simulations*n_trades*option["premium"]
    
    return {"sum_pl":sum(sum_pl), # total pl
            "avg_pl": np.mean(sum_pl), # mean pl
            "median_pl": np.median(sum_pl), # median pl
            "roi":np.mean(sum_pl)/(option["premium"]*n_trades), # roi
            "roi1":np.percentile(sum_pl,1)/(option["premium"]*n_trades), # roi 1% percentile
            "roi2.5":np.percentile(sum_pl,2.5)/(option["premium"]*n_trades), # roi 2.5% percentile
            "percent_win":100*sum([1 for x in pl_all if x > 0])/len(pl_all), # win percentage
            "p1_pl":np.percentile(sum_pl,1), # total pl 1% percentile
            "p2.5_pl":np.percentile(sum_pl,2.5), # total pl 2.5% percentile
            "p97.5_pl":np.percentile(sum_pl,97.5), # total pl 97.5% percentile
            "p99_pl":np.percentile(sum_pl,99) # total pl 99% percentile
            }
 
def DataTreatment(filename):
    """Loading Data and Treatment"""
    # load data
    data = pd.read_csv(filename,sep=",")
    
    # create datetime column
    dtDate = [datetime.strptime(data["Date"].values[i],"%b %d, %Y") for i in range(len(data))]
        
    data["dtDate"] = dtDate

    # strings to values
    if data["Price"].dtypes != "float64":
        data["Price"] = data["Price"].str.replace(",","").astype(float)
       
    if data["Open"].dtypes != "float64":
        data["Open"] = data["Open"].str.replace(",","").astype(float)
        
    if data["High"].dtypes != "float64":
        data["High"] = data["High"].str.replace(",","").astype(float)
    
    if data["Low"].dtypes != "float64":
        data["Low"] = data["Low"].str.replace(",","").astype(float)
    
    # add close variation
    close_var = [PerctChange(data.iloc[i+1,1],data.iloc[i,1]) for i in range(0,len(data)-1)]
    data["PriceVar"] = close_var + [np.NaN]
    
    return data

def GetOptionRoiInTimeWindow(time_window_in_days,time_offset_each_iter_in_days,time_offset_max_in_days):
    """Returns df with option's ROI in different time windows"""
    
    # get end and starting dates 
    end_dates = [current_time - dt.timedelta(days=i) for i in range(0,time_offset_max_in_days+time_offset_each_iter_in_days,time_offset_each_iter_in_days)]
    start_dates = [d - dt.timedelta(days=time_window_in_days) for d in end_dates]
    
    # check if lists have the same length
    if len(start_dates) != len(end_dates):
        print("Not enough data for the current start and end dates offset.")
    
    # copy original dataset
    data_subset = data.copy()
    
    # initialize vars
    min_roi = np.inf; min_dates = []; roi = []
    var = dict(); simulations_results = dict()
    
    # calculate options profitability for each time window
    # save minimum roi and respective dates
    for i in range(len(start_dates)):
        data_subset = data[(data["dtDate"] >= start_dates[i]) & (data["dtDate"] <= end_dates[i])]
        key = str(end_dates[i])
        
        for i_b,b in enumerate(BARRIERS):
            var[(key,i_b)] = GetVariationsFromBarrier(data_subset,option["strike"],b,(option["expiry_date"]-current_time).days)[0]
            simulations_results[(key,i_b)] = SimulateOptionProfitLoss(current_price,option,var[(key,i_b)],n_trades,n_simulations)
        
            roi.append([start_dates[i],end_dates[i],b,simulations_results[(key,i_b)]["roi1"],
                        simulations_results[(key,i_b)]["roi2.5"],simulations_results[(key,i_b)]["roi"],
                        simulations_results[(key,i_b)]["percent_win"]])
        
            if simulations_results[(key,i_b)]["roi"] < min_roi:
                min_roi = simulations_results[(key,i_b)]["roi"]
                min_dates = [str(start_dates[i]), key]
        
    print("Period with minimum ROI: ", min_dates, " ", min_roi)
    df_roi = pd.DataFrame(data=roi,columns=["StartDate","EndDate","Barrier","Roi1","Roi2.5","Roi","percent_win"])
    
    return df_roi

# =============================================================================
# TESTING FUNCTIONS
# =============================================================================
    
def Test1_GetVariationsFromBarrier(data,strike):
    # for barrier = 0 (0% change) and days_offset = 1, there should be as many non-null variations as in close_var
    var,days,date_base = GetVariationsFromBarrier(data,strike,0,1)
    close_var = [PerctChange(data.iloc[i+1,1],data.iloc[i,1]) for i in range(0,len(data)-1)
                 if (data.iloc[i,7] - data.iloc[i+1,7]).days <= 1]
    print("Non-null variations = %f, %f" % ( len([p for p in var if p != 0])/len(var), len(close_var)/len(var) ) )
  
def Test2_GetVariationsFromBarrier():
    # for strike = current price, option premium equal to 0, barrier equal to 0,
    # proportion of positive var should be similar to percentage_win
    option_test = option.copy()
    option_test["premium"] = 1e-6
    
    var,days,date_base = GetVariationsFromBarrier(data=data,strike=option["strike"],barrier=0,
                                                  days_offset=(option["expiry_date"]-datetime.now()).days)
    simulations_results = SimulateOptionProfitLoss(option["strike"],option,var,n_trades,n_simulations)
    print("Positive var proportion (strike = current_price) = %f Perct win = %f" %(GetProportion(var),simulations_results["percent_win"]))

# =============================================================================
# 
# =============================================================================
# =============================================================================
# MAIN CODE
# =============================================================================
# =============================================================================
#     
# =============================================================================
    
if __name__ == "__main__":
    # =============================================================================
    # INPUTS
    # =============================================================================
    
    # market data filename
    filename = "C:\\Users\\leocb\\Google Drive\\Python\\Options\\AEX Historical Data.csv"
    #filename = "C:\\Users\\X190284\\Documents\\Python\\Options\\Gold Futures Historical Data.csv"
    
    # market data
    current_price = 614.24
    current_time = datetime(2020,1,27)
    
    # option data
    option = { "is_american":True,
               "is_call":True,
               "strike":700,
               "premium":0.16,
               "expiry_date":datetime(2020,6,19)
               }
    
    # simulation parameters
    n_trades = 1000; n_simulations = 10
    
    # =============================================================================
    # LOADING DATA AND TREATMENT
    # =============================================================================
    
    data = DataTreatment(filename)
    
    # =============================================================================
    # USE ALL HISTORY
    # =============================================================================
      
    ## get variations for each considered barrier
    #var = [np.NaN]*len(BARRIERS); days = [np.NaN]*len(BARRIERS); date_base = [np.NaN]*len(BARRIERS)
    #
    #for i,b in enumerate(BARRIERS):
    #    print("strike = %f barrier = %f days_offset = %d " % (option["strike"],b,(option["expiry_date"]-current_time).days))
    #    var[i],days[i],date_base[i] = GetVariationsFromBarrier(data,option["strike"],b,(option["expiry_date"]-current_time).days)
    # 
    ## get profit/loss for each barrier
    #simulations_results = [np.NaN]*len(BARRIERS)
    #
    #for i,b in enumerate(BARRIERS):
    #    print("i = %d b = %f" % (i,b))
    #    simulations_results[i] = SimulateOptionProfitLoss(current_price,option,var[i],n_trades,n_simulations)
    #    
    #simulations_results[i] = SimulateOptionProfitLoss(current_price,option,var[i],n_trades,n_simulations)
    
    # =============================================================================
    # USE TIME WINDOWS
    # =============================================================================
    
    df_roi = GetOptionRoiInTimeWindow(time_window_in_days,time_offset_each_iter_in_days,time_offset_max_in_days)
    
    # =============================================================================
    # TESTS
    # =============================================================================
    
    Test1_GetVariationsFromBarrier(data,option["strike"])
    Test2_GetVariationsFromBarrier()
    # var,days,date_base = GetVariationsFromBarrier(data,option["strike"],1,30)