# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 17:00:23 2021

@author: leocb
"""

# =============================================================================
# TODO:
# - use API directly to find prices (website takes a long time to update)
# - average price is wrong in some cases (doesn't match the one in the page). Use the average shown in the page
# - add condition to look for prices X lower than all other items in the market
# - in refinables, use average price taken from the page itself
# - find bargains in price * amount for cheaper items
# =============================================================================

import pandas as pd
import os
import requests
import html
from bs4 import BeautifulSoup
import time
import locale
import winsound
import ctypes
from datetime import datetime

PRICE_MIN = 7e5
DIFF_MIN = 5e5
DELAY_BETWEEN_PAGES = 1
DELAY_BETWEEN_SEARCHES = 60*5
BEEP_FREQUENCY = 1500  # Set Frequency To 2500 Hertz
BEEP_DURATION = 500  # Set Duration To 1000 ms == 1 second

TAG_PRICE = "<td class=\"Price\">"
TAG_NAVSHOP = "value=\"@navshop "

# =============================================================================
# 
# =============================================================================

def get_str_between_substrs(str_to_search,substr1,substr2):
    pos_0 = str_to_search.find(substr1)
    pos_1 = str_to_search.find(substr2,pos_0)
    
    return str_to_search[pos_0+len(substr1):pos_1]

def find_bargains(df):
    
    items_bargains = []
    items_refinable = []
    str_output = ""
    len_df = len(df)
    
    for idx,row in df.iterrows():
        
        try:
            item_id = row["id"]
            # four_week_avg = row["four_week_avg"]
            one_week_avg = row["one_week_avg"]
            
            if one_week_avg <= 1:
                continue
            
            r = requests.get("http://www.originsro-market.de/sells/item_id/" + str(item_id))
            html_txt = html.unescape(r.text)
            
            soup = BeautifulSoup(html_txt,features="lxml")
            
            # check if it's a refinable item. If so, add item id to list
            if str(soup).find("style=\"color:#86cffe\">+1") > 0:
                items_refinable.append(item_id)
            
            # get item name
            item_name = row["name"]
            
            print("Searching " + item_name + " (" + str(idx+1) + "/" + str(len_df) + ")...\n")
            
            # print(soup.prettify())
            
            # a = soup.find("tbody", {"class":"list"})
            
            try:
                list_prices = soup.findAll('tbody')[1]
            except:
                print("No shops found for " + item_name + ".\n")
                continue
            
            children = list_prices.findChildren("tr",recursive=False)
            
            for child in children:
                str_child = str(child)
                
                # get seller
                get_str_between_substrs(str(soup.title),"Originsro - "," detail")
                
                # pos_0 = str_child.find(TAG_NAVSHOP)
                # pos_1 = str_child.find("\">",pos_0)
                
                seller_name = "@navshop " + get_str_between_substrs(str_child,TAG_NAVSHOP,"\">")
                
                # print(str_child[pos_0+len_tag_navshop:pos_1])
                
                # get price
                price = float(get_str_between_substrs(str_child,TAG_PRICE,"</td>").replace(",",""))
                
                # if four_week_avg - price >= DIFF_MIN:
                #     print(item_name + " " + str(price) + " " + seller_name + " - " + str(four_week_avg - price) + 
                #           "z cheaper than 4 week average.\n")
                
                if one_week_avg - price >= DIFF_MIN:
                    print(item_name + " " + str(price) + " " + seller_name + " - " + locale.format_string("%d",one_week_avg - price,grouping=True) + 
                          "z cheaper than 1 week average.\n")
                    str_output += item_name + " " + str(price) + " " + seller_name + " - " + locale.format_string("%d",one_week_avg - price,grouping=True) + "z cheaper than 1 week average.\n"
                    items_bargains.append([item_id,price])
                
                # print(str_child[pos_0+len_tag_price:pos_1])
                
                # print(child)
            
            time.sleep(DELAY_BETWEEN_PAGES)
        except Exception as err_inst:
                print(err_inst)
                continue
            
    return items_bargains, items_refinable, str_output
    
def find_refinables_bargains(df):
    
    items_bargains = []
    
    for idx,row in df.iterrows():
        
        try:
            item_id = row["id"]
            # four_week_avg = row["four_week_avg"]
            one_week_avg = row["one_week_avg"]
            
            if one_week_avg <= 1:
                continue
            
            for r in range(1,11):
                r = requests.get("http://www.originsro-market.de/sells/item_id/" + str(item_id) + "/" + str(r))
                html_txt = html.unescape(r.text)
                
                soup = BeautifulSoup(html_txt,features="lxml")
                
                # check if it's a refinable item. If so, add item id to list
                if str(soup).find("style=\"color:#86cffe\">+1") > 0:
                    items_refinable.append(item_id)
                
                # get item name
                item_name = get_str_between_substrs(str(soup.title),"Originsro - "," detail")
                
                print("Searching " + item_name + "...\n")
                
                # print(soup.prettify())
                
                # a = soup.find("tbody", {"class":"list"})
                
                try:
                    list_prices = soup.findAll('tbody')[1]
                except:
                    print("No shops found for " + item_name + ".\n")
                    continue
                
                len_tag_price = len(TAG_PRICE)
                len_tag_navshop = len(TAG_NAVSHOP)
                
                children = list_prices.findChildren("tr",recursive=False)
                
                for child in children:
                    str_child = str(child)
                    
                    # get seller
                    get_str_between_substrs(str(soup.title),"Originsro - "," detail")
                    
                    # pos_0 = str_child.find(TAG_NAVSHOP)
                    # pos_1 = str_child.find("\">",pos_0)
                    
                    seller_name = "@navshop " + get_str_between_substrs(str_child,TAG_NAVSHOP,"\">")
                    
                    # print(str_child[pos_0+len_tag_navshop:pos_1])
                    
                    # get price
                    price = float(get_str_between_substrs(str_child,TAG_PRICE,"</td>").replace(",",""))
                    
                    # if four_week_avg - price >= DIFF_MIN:
                    #     print(item_name + " " + str(price) + " " + seller_name + " - " + str(four_week_avg - price) + 
                    #           "z cheaper than 4 week average.\n")
                    
                    if one_week_avg - price >= DIFF_MIN:
                        print(item_name + " " + str(price) + " " + seller_name + " - " + locale.format_string("%d",one_week_avg - price,grouping=True) + 
                              "z cheaper than 1 week average.\n")
                        items_bargains.append(item_id)
                    
                    # print(str_child[pos_0+len_tag_price:pos_1])
                    
                    # print(child)
                
                time.sleep(DELAY_BETWEEN_PAGES)
        except Exception as err_inst:
                print(err_inst)
                continue
                
    return items_bargains

# =============================================================================
# 
# =============================================================================

locale.setlocale(locale.LC_ALL, 'en_US')

# change dir
os.chdir("C:\\Users\\leocb\\Documents\\Python\\OriginsRO market")

# read items
items = pd.read_csv("oro_market.csv")

# filter price and eggs
items_filter = items[(items.one_week_avg >= PRICE_MIN) & ~(items["name"].astype(str).str.contains(" Egg"))]

# items_filter = items_filter[items_filter.id==2619]

previous_items = []
first_run = True
        
# find regular items bargains
while(True):
    items_bargains, items_refinable, out = find_bargains(items_filter.reset_index(drop=True))
    new_items = [item for item in items_bargains if not item in previous_items]
    previous_items = items_bargains
    
    print("===================================\n")
    print(out)
    print("===================================\n")
    
    if len(new_items) > 0 and not first_run:
        winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
        winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
        ctypes.windll.user32.MessageBoxW(0, "New bargain found at " + str(datetime.now()), "New bargain found", 1)

    print("Standing by for " + str(DELAY_BETWEEN_SEARCHES) + " seconds...")
    first_run = False
    time.sleep(DELAY_BETWEEN_SEARCHES)

# items_bargains, items_refinable, out = find_bargains(items_filter.reset_index(drop=True))

# # find refinable items bargains
# items_refinables = items_filter[items_filter["id"].isin(items_refinable)]
# items_refinables_bargains = find_refinables_bargains(items_refinables)


        
# for row in rows:
#     cells = row.find_all("td")
#     rn = cells[0].get_text()
#     print(rn)
#     # and so on

# comodo = 

# for item_id in ids:
    
    
#     headers = {"x-api-key":API_KEY}

#     requestResponse = requests.get("https://api.originsro.org/api/v1/market/list",
#                                    headers=headers)

