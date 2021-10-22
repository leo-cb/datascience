# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 17:37:45 2018

@author: Leonardo
"""

import requests
import json
#import googlefinance.client as google
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
#from mpl_finance import candlestick_ohlc
import pandas as pd
from time import sleep
import os
import matplotlib
from matplotlib import style

# Intrinio credentials
USERNAME = "insert_username_here"
PASSWORD = "insert_password_here"

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 8,
        }

class CompanyBasics:
    def __init__(self,ticker):
        page = requests.get('https://www.wsj.com/market-data/'+ticker+'/company-people/')
        self.content = page.text
    
    def getDescription(self):
        """Get description from company profile page"""
        content = self.content
        
        # find title
        pos = content.find("<h3>Description") 
        
        # return None if string wasn't found
        if pos < 0:
            return None
    
        # find next string
        startStr = "<p class=\"txtBody\">"
        pos = content.find(startStr,pos)
        
        # return None if string wasn't found
        if pos < 0:
            return None

        # get tag's end position
        finalPos = content.find("</p>",pos)
        
        # return None if string wasn't found
        if finalPos < 0:
            return None
        
        # return scraped value
        return content[pos+len(startStr):finalPos].replace("+","")
    
    def getSector(self):
        """Get sector from company profile page"""
        content = self.content
        
        # find str
        startStr = "<span class=\"data_lbl\">Sector</span> <span class=\"data_data\">"
        pos = content.find(startStr) 
        
        # return None if string wasn't found
        if pos < 0:
            return None

        # get tag's end position
        finalPos = content.find("</span>",pos+len(startStr))
        
        # return None if string wasn't found
        if finalPos < 0:
            return None
        
        # return scraped value
        return content[pos+len(startStr):finalPos]
    
    def getIndustry(self):
        """Get industry from company profile page"""
        content = self.content
        
        # find str
        startStr = "<span class=\"data_lbl\">Industry</span> <span class=\"data_data\">"
        pos = content.find(startStr) 
        
        # return None if string wasn't found
        if pos < 0:
            return None

        # get tag's end position
        finalPos = content.find("</span>",pos+len(startStr))
        
        # return None if string wasn't found
        if finalPos < 0:
            return None
        
        # return scraped value
        return content[pos+len(startStr):finalPos]
    
class CompanyProfile:
    def __init__(self,ticker):
        page = requests.get('https://www.wsj.com/market-data/'+ticker+'/financials/')
        self.content = page.text
    
    def getValues(self,title):
        """Get values from title in financials page"""
        content = self.content
        
        # find title
        pos = content.find(title) 
        
        # return None if string wasn't found
        if pos < 0:
            return None
    
        # find next string
        pos = content.find("deltaType",pos)
        
        # return None if string wasn't found
        if pos < 0:
            return None
        
        # find next string
        pos = content.find(">",pos)
        
        # return None if string wasn't found
        if pos < 0:
            return None
        
        finalPos = content.find("</span>",pos)
        
        # return None if string wasn't found
        if finalPos < 0:
            return None
        
        # return None if there is no estimate
        if content[pos+1:finalPos] == "-":
            return None
        
        # return scraped value
        return float(content[pos+1:finalPos])
        
class CompanyAccounting:
    def __init__(self,ticker,sheet,period="annual"):
        self.period = period
        page = requests.get('https://www.wsj.com/market-data/'+ticker+'/financials/'+period+'/'+sheet)
        self.content = page.text
    
    def getValues(self,title):
        """Get values associated with a given fundamental"""
        content = self.content
        
        values = dict()
        posTitle = content.find("<td class>"+title+"</td>")
        
        # return empty dict if string wasn't found
        if posTitle < 0:
            return dict()
        
        baseIndex = posTitle
        
        # today's date
        now = datetime.now()
        
        # annual
        if self.period == "annual":
            
            # get previous year
            year = now.year-1 
            
            for y in range(year,year-5,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                    
                values[y] = float(val)   
                
        # quarterly
        elif self.period == "quarter":
            
            for q in range(4,-1,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                
                values[q] = float(val)  
        else:
            return dict()
        
        return values
    
    def getIndentedValues(self,title):
        """Get values associated with a given fundamental"""
        content = self.content
        
        values = dict()
        posTitle = content.find("<td class=\"indent\">"+title+"</td>")
        
        # return empty dict if string wasn't found
        if posTitle < 0:
            return dict()
        
        baseIndex = posTitle
        
        # today's date
        now = datetime.now()
        
        # annual
        if self.period == "annual":
            
            # get previous year
            year = now.year-1 
            
            for y in range(year,year-5,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                    
                values[y] = float(val)   
                
        # quarterly
        elif self.period == "quarter":
            
            for q in range(4,-1,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                
                values[q] = float(val)  
        else:
            return dict()
        
        return values
    
def makeReq(url):
    return requests.get(url,auth=(USERNAME,PASSWORD))

def addToDict(dictionary,key,value):
    if key not in dictionary:
        dictionary[key] = value
    else:
        dictionary[key].append(value)

def getCompanyFundamentals(ticker,item):
    r = makeReq("https://api.intrinio.com/historical_data?identifier=" + 
                ticker + "&item=" + item)
    info = json.loads(r.text)
    return info 

def getCompanyFundamentalsAsTimeseries(ticker,item):
    dataDict = getCompanyFundamentals(ticker,item)
    ts = parseToTimeseries(dataDict["data"])
    
    return ts

def fillCompanies(dictionary,ticker,items):
    dataDict = dict()
    for item in items:
        r = makeReq("https://api.intrinio.com/historical_data?identifier=" + 
                    ticker + "&item=" + item)
        info = json.loads(r.text)
        dataDict[item] = info["data"]
        
    addToDict(dictionary,ticker,dataDict)
    return dictionary

def getTechnicalsAlpha(ticker,interval):
    API_KEY = "1I40VWU6X242ZFVE"
    if interval == True: # daily
        r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="+ticker+"&apikey="+API_KEY)
    else:    
        r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol="+ticker+"&apikey="+API_KEY)
    
    return r.text
 
# =============================================================================
# def getTechnicals(ticker,interval):
#     
#     param = {
#         'q': ticker, # Stock symbol (ex: "AAPL")
#         'i': interval, # Interval size in seconds ("86400" = 1 day intervals)
#         'p': "8Y" # Period (Ex: "1Y" = 1 year)
#     }
#     
#     return google.get_price_data(param) 
# =============================================================================

def parseToTimeseries(data): # data is a list of dictionaries {'date':'YYYY-MM-DD','value':val}
    time = list()
    val = list()
    
    for dictionary in data:
        time.append(datetime.strptime(dictionary["date"],"%Y-%m-%d"))
        val.append(dictionary["value"])
    
    return (time,val)

def jsonToDf(data,keyName):
    """Transforms an Alpha Vantage json response to a dataframe"""
    # check if data has keyName as key
    if keyName not in data:
        return (pd.DataFrame())
    
    # place prices and open times in lists
    ohlcv = list()
    openTime = list()
    for t,prices in data[keyName].items():
        ohlcv.append([float(prices["1. open"]),float(prices["2. high"]),float(prices["3. low"])
                    ,float(prices["4. close"]),float(prices["5. volume"])])
        openTime.append(datetime.strptime(t,"%Y-%m-%d"))
        
    # create df using previously created lists
    df = pd.DataFrame(data=ohlcv,columns=["Open","High","Low","Close","Volume"],index=openTime)
    
    return df

def getStocksData(stocks, is_daily = False):
    """Returns stocks data in a dict of dataframes"""
    
    stocksDict = dict()
    
    if not is_daily:
        ts_name = "Weekly Time Series"
    else:
        ts_name = "Time Series (Daily)"
    
    for stock in stocks:
        # get OHLCV data from server
        req = getTechnicalsAlpha(stock, is_daily)
        
        if req == False:
            continue
        
        # load request to a dictionary
        data = json.loads(req)
        
        # place dataframe in the dictionary
        df = jsonToDf(data,ts_name)
        
        if not df.empty:
            stocksDict[stock] = df
        
        sleep(0.3)
        
    return stocksDict
 
def FindResistance(highs,offset,start):
    """
    Finds nearest resistance with offset 'offset' and starting from 'start' index 
    """
    
    isThisResistance = bool()
    
    for i in range(offset+start,len(highs)-offset):
        isThisResistance = True
        resistanceIndex = i
        
        for j in range(start,offset):
            if highs[i] < highs[i+j] or highs[i] < highs[i-j]:
                isThisResistance = False
                break
            
        if isThisResistance:
            break
    
    if isThisResistance:
        return (resistanceIndex,highs[resistanceIndex])
    else:
        return (None,None)

def FindSupport(lows,offset,start):
    """
    Finds nearest support with offset 'offset' and starting from 'start' index 
    """
    
    isThisSupport = bool()
    
    for i in range(offset+start,len(lows)-offset):
        isThisSupport = True
        supportIndex = i
        
        for j in range(start,offset):
            if lows[i] > lows[i+j] or lows[i] > lows[i-j]:
                isThisSupport = False
                break
            
        if isThisSupport:
            break
    
    if isThisSupport:
        return (supportIndex,lows[supportIndex])
    else:
        return (None,None)
    
def datetime64ToDatetime(d64list):
    d = list()
    for timestamp in d64list.tolist():
        ts = timestamp*10**-9
        d.append(datetime.fromtimestamp(ts))
    
    return d

class CompanyAccountingScrapper:
    def __init__(self,ticker,period="annual"):
        self.period = period
        
        self.content = {"income-statement":requests.get('https://www.wsj.com/market-data/quotes/'+ticker+'/financials/'+period+'/income-statement').text,
                        "balance-sheet":requests.get('https://www.wsj.com/market-data/quotes/'+ticker+'/financials/'+period+'/balance-sheet').text,
                        "cash-flow":requests.get('https://www.wsj.com/market-data/quotes/'+ticker+'/financials/'+period+'/cash-flow').text}

    def getValues(self,title,sheet):
        """Get values associated with a given fundamental"""
        
        content = self.content[sheet]
        
        values = dict()
        posTitle = content.find("<td class>"+title+"</td>")
        
        # return empty dict if string wasn't found
        if posTitle < 0:
            return dict()
        
        baseIndex = posTitle
        
        # today's date
        now = datetime.now()
        
        # annual
        if self.period == "annual":
            
            # get previous year
            year = now.year-1 
            
            for y in range(year,year-5,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # if value is just an hifen "-", return empty dict
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                    
                values[y] = float(val)   
                
        # quarterly
        elif self.period == "quarter":
            
            for q in range(4,-1,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                
                values[q] = float(val)  
        else:
            return dict()
        
        return values
    
    def getIndentedValues(self,title,sheet):
        """Get values associated with a given fundamental"""
        content = self.content[sheet]
        
        values = dict()
        posTitle = content.find("<td class=\"indent\">"+title+"</td>")
        
        # return empty dict if string wasn't found
        if posTitle < 0:
            return dict()
        
        baseIndex = posTitle
        
        # today's date
        now = datetime.now()
        
        # annual
        if self.period == "annual":
            
            # get previous year
            year = now.year-1 
            
            for y in range(year,year-5,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                    
                values[y] = float(val)   
                
        # quarterly
        elif self.period == "quarter":
            
            for q in range(4,-1,-1):
                # tag before value
                posValue = content.find("<td class>",baseIndex+1)
                
                # this will be the next base index to start search from
                baseIndex = content.find("</td>",posValue)
                
                # remove commas and hifens
                val = content[posValue+10:baseIndex].replace(",","").replace("-","0")
                
                # negative values
                if val.find("(") > -1:
                    # remove ()
                    val = val.replace("(","").replace(")","")
                    
                    # add minus before value
                    val = "-"+val
                
                values[q] = float(val)  
        else:
            return dict()
        
        return values
    
def perctChange(v1,v2):
    return 100*(v1-v2)/abs(v2)