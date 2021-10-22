# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 20:22:51 2018

@author: Leonardo
"""

#todo:
#    - às vezes não faz load de fundamentais: é preciso ver tamanho da página
#    - as vezes não faz load de ohlcv
#    - incluir market cap, PE, PEG, ROIC como colunas

from functions import CompanyAccountingScrapper,getTechnicalsAlpha,getStocksData,\
FindSupport,FindResistance,CompanyBasics,CompanyProfile

from datetime import datetime
from time import sleep
import pandas as pd

# =============================================================================
# MACROS
# =============================================================================
BENCHMARK_TICKER = "SPY"

def nearest(items, pivot):
    """Returns the datetime in items which is the closest to the date pivot"""
    return min(items, key=lambda x: abs(x - pivot))

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

def perctChange(v1,v2):
    return (v1-v2)/abs(v2)
    
class CompanyMetrics(CompanyAccountingScrapper):
    def __init__(self,ticker,period="annual"):
        
        CompanyAccountingScrapper.__init__(self,ticker,period)
        
        if period == "annual":
            self.indices = range(datetime.now().year-5,datetime.now().year)
        else:
            self.indices = range(0,5)
        
        # income values
        self.revenue = self.getValues("Sales/Revenue","income-statement")
        self.gross_income = self.getValues("Gross Income","income-statement")
        self.net_income = self.getValues("Net Income","income-statement")
        self.shares = self.getValues("Basic Shares Outstanding","income-statement")
        self.sga = self.getValues("SG&amp;A Expense","income-statement")
        self.ebit = self.getEbit()
        self.rdexpense = self.getIndentedValues("Research &amp; Development","income-statement")
        self.interest = self.getValues("Interest Expense","income-statement")

        # balance values
        self.receivables = self.getValues("Total Accounts Receivable","balance-sheet")
        self.inventories = self.getValues("Inventories","balance-sheet")
        self.lt_debt = self.getValues("Long-Term Debt","balance-sheet")
        self.equity = self.getValues("Total Equity","balance-sheet")
        self.current_assets = self.getValues("Total Current Assets","balance-sheet")
        self.current_liabilities = self.getValues("Total Current Liabilities","balance-sheet")
        
        # cash flow values
        self.operating_cf = self.getValues("Net Operating Cash Flow","cash-flow")
        self.free_cf = self.getValues("Free Cash Flow","cash-flow")
        self.capital_exp = self.getValues("Capital Expenditures","cash-flow")
       
    def getGrossIncome(self):
        return self.gross_income
    
    def getEbit(self):
        self.ebit = dict()
        
        for i in self.indices:
            if i in self.sga.keys() and i in self.gross_income.keys():
                self.ebit[i] = self.gross_income[i] - self.sga[i]
            
        return self.ebit
    
    def getEps(self):
        try:
            if (len(self.eps) > 0):
                return self.eps
        except:
            self.eps = dict()
        
        for i in self.indices:
            if i in self.net_income.keys() and i in self.shares.keys() and \
            self.shares[i] != 0:
                self.eps[i] = self.net_income[i]/self.shares[i]
        
        return self.eps
        
    def getEpsGrowth(self):
        eps_growth = dict()
        self.eps = self.getEps()
        
        if len(self.eps) == 0:
            return dict()
        
        for i in range(min(self.eps.keys())+1,max(self.eps.keys())+1):
            if self.eps[i-1] != 0:
                eps_growth[i] = perctChange(self.eps[i],self.eps[i-1])
        
        return eps_growth

    def getRevenue(self):
        return self.revenue
    
    def getRevenueGrowth(self):
        rev_growth = dict()
        
        try:
            if len(self.revenue) == 0:
                return dict()
        except:
            return dict()
            
        for i in range(min(self.revenue.keys())+1,max(self.revenue.keys())+1):
            if self.revenue[i-1] != 0:
                rev_growth[i] = perctChange(self.revenue[i],self.revenue[i-1])
        
        return rev_growth
    
    def getGrossMargin(self):
        gross_margin = dict()
        
        try:
            if len(self.revenue) == 0 or len(self.gross_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.revenue.keys() and i in self.gross_income.keys()\
            and self.revenue[i] != 0:
                gross_margin[i] = self.gross_income[i]/self.revenue[i]
        
        return gross_margin
        
    def getOperatingMargin(self):
        operating_margin = dict()
        
        try:
            if len(self.revenue) == 0 or len(self.net_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.revenue.keys() and i in self.net_income.keys()\
            and self.revenue[i] != 0:
                operating_margin[i] = self.net_income[i]/self.revenue[i]
        
        return operating_margin
        
    def getRdExpenseToGross(self):
        ratio = dict()
        
        try:
            if len(self.rdexpense) == 0 or len(self.gross_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.rdexpense.keys() and i in self.gross_income.keys()\
            and self.gross_income[i] != 0:
                ratio[i] = self.rdexpense[i]/self.gross_income[i]
        
        return ratio
    
    def getInterestToEbit(self):
        ratio = dict()
        
        try:
            if len(self.interest) == 0 or len(self.ebit) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.interest.keys() and i in self.ebit.keys()\
            and self.ebit[i] != 0:
                ratio[i] = self.interest[i]/self.ebit[i]
        
        return ratio

    def getQuickRatio(self):
        ratio = dict()
        
        try:
            if len(self.current_assets) == 0 or len(self.inventories) == 0\
            or len(self.current_liabilities) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.current_assets.keys() and i in self.inventories.keys()\
            and i in self.current_liabilities.keys() and self.current_liabilities[i] != 0:
                ratio[i] = (self.current_assets[i]-self.inventories[i])/self.current_liabilities[i]
        
        return ratio
    
    def getReceivInventToRev(self):
        ratio = dict()
        
        try:
            if len(self.receivables) == 0 or len(self.inventories) == 0\
            or len(self.revenue) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.receivables.keys() and i in self.inventories.keys()\
            and i in self.revenue.keys() and self.revenue[i] != 0:
                ratio[i] = (self.receivables[i]+self.inventories[i])/self.revenue[i]
        
        return ratio
    
    def getLtDebtToEquity(self):
        ratio = dict()
        
        try:
            if len(self.lt_debt) == 0 or len(self.equity) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.lt_debt.keys() and i in self.equity.keys()\
            and self.equity[i] != 0:
                ratio[i] = self.lt_debt[i]/self.equity[i]
        
        return ratio
    
    def getOperatingToIncome(self):
        ratio = dict()
        
        try:
            if len(self.operating_cf) == 0 or len(self.net_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.operating_cf.keys() and i in self.net_income.keys()\
            and self.net_income[i] != 0:
                ratio[i] = self.operating_cf[i]/self.net_income[i]
        
        return ratio
    
    def getFcfToIncome(self):
        ratio = dict()
        
        try:
            if len(self.free_cf) == 0 or len(self.net_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.free_cf.keys() and i in self.net_income.keys()\
            and self.net_income[i] != 0:
                ratio[i] = self.free_cf[i]/self.net_income[i]
        
        return ratio
    
    def getCapitalExpToIncome(self):
        ratio = dict()
        
        try:
            if len(self.capital_exp) == 0 or len(self.net_income) == 0:
                return dict()
        except:
            return dict()
        
        for i in self.indices:
            if i in self.capital_exp.keys() and i in self.net_income.keys()\
            and self.net_income[i] != 0:
                ratio[i] = abs(self.capital_exp[i])/self.net_income[i]
        
        return ratio

def fillDict(a_dict,missing_keys,fill=None):
    ret_dict = dict()
    
    if type(a_dict) != dict or len(a_dict) == 0:
        return {missing_keys[i]:None for i in range(len(missing_keys))}
    
    for k in sorted(missing_keys):
        if k in a_dict.keys():
            ret_dict[k] = a_dict[k]
        else:
            ret_dict[k] = fill
    
    return ret_dict
    
def dictToList(a_dict, ascending = True):
    """Returns a list filled with dictionary elements, sorted by key,
    filling out missing keys inbetween the minimum and maximum key with 'None'"""
    
    a_list = list()

    for k in sorted(list(range(min(a_dict.keys()),max(a_dict.keys())+1)),
                    reverse = not ascending):
        if k in a_dict.keys():
            a_list.append(a_dict[k])
        else:
            a_list.append(None)
    
    return a_list

def sliceDict(a_dict,a_slice):
    ret_list = list()
    
    for i in a_slice:
        if i in a_dict.keys():
            ret_list.append(a_dict[i])
        else:
            ret_list.append(None)
        
    return ret_list
    
m = CompanyAccountingScrapper("AAON")
m.getValues("Long-Term Debt","balance-sheet")

# read stocks from NASDAQ
file = pd.read_table("nasdaqlisted.txt","|")
stocks = file["Symbol"].tolist()

# read stocks from NYSE
file = pd.read_table("NYSE.txt","\t")
stocks += file["Symbol"].tolist()

# get benchmark
benchmark = getStocksData([BENCHMARK_TICKER])[BENCHMARK_TICKER]

# get tickers OHLCV
#tickers = getStocksData(stocks[:10])
#tickers = getStocksData(stocks[80:95])

# current year
year_today = datetime.now().year

# list to save performance to
stock_data = list()

years_all = list(range(year_today-5,year_today))
years_growth = list(range(year_today-4,year_today))
years_avg = list(range(year_today-3,year_today))

content = dict()

for s in stocks[80:95]:
    
    # load stock ohlcv data
    ohlcv = getStocksData([s])[s]
    
    # initialize company metrics
    metrics = CompanyMetrics(s)

    # get sector and industry
    sector = None; industry = None; j = 0
    while (sector == None and industry == None and j < 3):
        profile = CompanyBasics(s)
        sector = profile.getSector()
        industry = profile.getIndustry()
        sleep(0.1)
        j += 1
    
    # calculate income statement metrics
    eps = fillDict(metrics.getEps(),years_all)
    eps_growth = fillDict(metrics.getEpsGrowth(),years_growth)
    eps_avg_growth = fillDict({y:perctChange(eps[y],eps[y-2])/2 \
                               for y in range(year_today-3,year_today)\
                               if eps[y] != None and eps[y-2] != None\
                               and eps[y-2] != 0},years_avg)
        
    rev = fillDict(metrics.getRevenue(),years_all)
    rev_growth = fillDict(metrics.getRevenueGrowth(),years_growth)
    
    rev_avg_growth = fillDict({y:perctChange(rev[y],rev[y-2])/2 \
                               for y in range(year_today-3,year_today)\
                               if rev[y] != None and rev[y-2] != None\
                               and rev[y-2] != 0},years_avg)
    
    gross_margin = fillDict(metrics.getGrossMargin(),years_all)
    operating_margin = fillDict(metrics.getOperatingMargin(),years_all)
    rdexpense_to_gross = fillDict(metrics.getRdExpenseToGross(),years_all)
    interest_to_ebit = fillDict(metrics.getInterestToEbit(),years_all)
    
    # calculate balance sheet metrics
    quick_ratio = fillDict(metrics.getQuickRatio(),years_all)
    receiv_invent_to_rev = fillDict(metrics.getReceivInventToRev(),years_all)
    receiv_invent_to_rev_growth = fillDict({y:perctChange(receiv_invent_to_rev[y],receiv_invent_to_rev[y-1]) \
                                           for y in range(year_today-4,year_today)\
                                           if receiv_invent_to_rev[y] != None\
                                           and receiv_invent_to_rev[y-1] != None\
                                           and receiv_invent_to_rev[y-1] != 0},years_growth)
        
    receiv_invent_to_rev_avg_growth = fillDict({y:perctChange(receiv_invent_to_rev[y],receiv_invent_to_rev[y-2])/2 \
                                               for y in range(year_today-3,year_today)\
                                               if receiv_invent_to_rev[y] != None\
                                               and receiv_invent_to_rev[y-2] != None\
                                               and receiv_invent_to_rev[y-2] != 0},years_avg)
    
    lt_debt_to_equity = fillDict(metrics.getLtDebtToEquity(),years_all)
    
    # calculate cash flow metrics
    ocf_to_income = fillDict(metrics.getOperatingToIncome(),years_all)
    ocf_to_income_avg = fillDict({y:(ocf_to_income[y-2]+ocf_to_income[y-1]+ocf_to_income[y])/3\
                                  for y in range(year_today-3,year_today)\
                                  if ocf_to_income[y] != None and ocf_to_income[y-1] != None\
                                  and ocf_to_income[y-2] != None},years_avg)
    
    fcf_to_income = fillDict(metrics.getFcfToIncome(),years_all)
    
    fcf_to_income_avg = fillDict({y:(fcf_to_income[y-2]+fcf_to_income[y-1]+fcf_to_income[y])/3\
                                  for y in range(year_today-3,year_today)\
                                  if fcf_to_income[y] != None and fcf_to_income[y-1] != None\
                                  and fcf_to_income[y-2] != None},years_avg)
        
    capital_exp_to_income = fillDict(metrics.getCapitalExpToIncome(),years_all)
    
    capital_exp_to_income_avg = fillDict({y:(capital_exp_to_income[y-2]+capital_exp_to_income[y-1]+capital_exp_to_income[y])/3\
                                          for y in range(year_today-3,year_today)\
                                          if capital_exp_to_income[y] != None and capital_exp_to_income[y-1] != None\
                                          and capital_exp_to_income[y-2] != None},years_avg)
    
    content[s] = str(metrics.content)
    
    for y in range(year_today-2,year_today):
        ttm = datetime(y,2,1,0,0)
        now = datetime(y+1,2,1,0,0)
        performance = perctChange(getPriceNearDate(ohlcv,"Close",now),
                                  getPriceNearDate(ohlcv,"Close",ttm))
        performance_bmrk = perctChange(getPriceNearDate(ohlcv,"Close",now),
                           getPriceNearDate(ohlcv,"Close",ttm))\
                           /perctChange(getPriceNearDate(benchmark,"Close",now),
                           getPriceNearDate(benchmark,"Close",ttm))
        
        stock_data.append([s,y+1,sector,industry,performance,performance_bmrk] 
                          + sliceDict(eps,list(range(y-3,y)))\
                          + sliceDict(eps_growth,list(range(y-2,y)))\
                          + sliceDict(eps_avg_growth,list(range(y-1,y)))\
                          + sliceDict(rev,list(range(y-3,y)))\
                          + sliceDict(rev_growth,list(range(y-2,y)))\
                          + sliceDict(rev_avg_growth,list(range(y-1,y)))\
                          + sliceDict(gross_margin,list(range(y-3,y)))\
                          + sliceDict(operating_margin,list(range(y-3,y)))\
                          + sliceDict(rdexpense_to_gross,list(range(y-3,y)))\
                          + sliceDict(interest_to_ebit,list(range(y-3,y)))\
                          + sliceDict(quick_ratio,list(range(y-3,y)))\
                          + sliceDict(receiv_invent_to_rev,list(range(y-3,y)))\
                          + sliceDict(receiv_invent_to_rev_growth,list(range(y-2,y)))\
                          + sliceDict(receiv_invent_to_rev_avg_growth,list(range(y-1,y)))\
                          + sliceDict(lt_debt_to_equity,list(range(y-3,y)))\
                          + sliceDict(ocf_to_income,list(range(y-3,y)))\
                          + sliceDict(ocf_to_income_avg,list(range(y-1,y)))\
                          + sliceDict(fcf_to_income,list(range(y-3,y)))\
                          + sliceDict(fcf_to_income_avg,list(range(y-1,y)))\
                          + sliceDict(capital_exp_to_income,list(range(y-3,y)))\
                          + sliceDict(capital_exp_to_income_avg,list(range(y-1,y))))
        
# df to save performance in
stocks_df = pd.DataFrame(stock_data,columns=["Ticker","BaseYear","Sector","Industry","Performance","PerformanceToBenchmark","EPSY3","EPSY2","EPSY1","EPSGwthY2",
                                             "EPSGwthY1","EPSAvgGwth","RevY3","RevY2","RevY1","RevGwthY2","RevGwthY1","RevAvgGwth","GrossMarginY3","GrossMarginY2",
                                             "GrossMarginY1","OperatingMarginY3","OperatingMarginY2","OperatingMarginY1","RDExpenseToGrossY3",
                                             "RDExpenseToGrossY2","RDExpenseToGrossY1","InterestToEbitY3","InterestToEbitY2","InterestToEbitY1",
                                             "QuickRatioY3","QuickRatioY2","QuickRatioY1","RIToRevY3","RIToRevY2","RIToRevY1","RIToRevGwthY2","RIToRevGwthY1",
                                             "RIToRevAvgGwth","LTDebtToEquityY3","LTDebtToEquityY2","LTDebtToEquityY1","OCFToIncomeY3","OCFToIncomeY2",
                                             "OCFToIncomeY1","OCFToIncomeAvg","FCFToIncomeY3","FCFToIncomeY2","FCFToIncomeY1","FCFToIncomeAvg",
                                             "CapitalExpToIncomeY3","CapitalExpToIncomeY2","CapitalExpToIncomeY1","CapitalExpToIncomeAvg"])     