import os
import requests
import matplotlib.pyplot as plt
from matplotlib import rcParams
import json
from datetime import datetime
from tabulate import tabulate
import numpy as np

os.system("cls")

#dictionary linking time to time interval
time_dict = {
  'max': '1mo',
  '5y': '1wk',
  '1y': '1d',
  'ytd': '1d',
  '6mo': '1d',
  '1mo': '1h',
  '5d': '5m',
  '1d': '1m'
}

#the loop is to allow error proofing
while True:

  try:#try this
    ticker = input("Please input the ticker symbol: ").upper()#input stock name
    time = input ("time: max, 5y, 1y, ytd, 6mo, 1mo, 5d, 1d: ").lower()#input time range you wanna view on graph
    
    url = "https://yh-finance.p.rapidapi.com/stock/v3/get-chart"#this part of the API had some of the endpoints I wanted
    
    #What info to grab from API
    querystring = {"interval":time_dict[time],"symbol":ticker,"range":time,"region":"US","includePrePost":"false","useYfid":"true","includeAdjustedClose":"false","events":"capitalGain,div,split"}
    
    headers = {
      "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
      "X-RapidAPI-Key": "e23a0e64d0msh16f52502108c2c1p1cb33djsn6c362890fd98"
    }
    
    response1 = requests.request("GET", url, headers=headers, params=querystring)#getting all info from API
  
  
    json_obj1= json.loads(response1.text)
    json_result_skip = json_obj1['chart']['result'][0]#skip to make code cleaner
    json_quote_skip = json_result_skip["indicators"]["quote"][0]
    json_volume = json_quote_skip["volume"]#grab volume 
    json_close = json_quote_skip["close"]#grab all closing prices from indicated time range at every interval
    json_time = json_result_skip["timestamp"]#grab all time stamps
    date_time = [datetime.fromtimestamp(n) for n in json_time]#convert time stamp to readable date
    
    y = json_close#y of graph
    x = date_time#x of graph
    break

  except KeyError:#if this error happens
    os.system("cls")
    print("Invalid Time Range")

  except:#if any other error happens
    os.system("cls")
    print("Invalid Ticker")


url = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"#this part of the API had the other endpoints I wanted

querystring = {"symbol":ticker,"region":"US"}#what data to grab from API

headers = {
  "X-RapidAPI-Key": "e23a0e64d0msh16f52502108c2c1p1cb33djsn6c362890fd98",
  "X-RapidAPI-Host": "yh-finance.p.rapidapi.com"
}

response2 = requests.request("GET", url, headers=headers, params=querystring)#grab data from API

json_obj2 = json.loads(response2.text)
json_skip = json_obj2['summaryDetail']#skip to make code cleaner
json_yield = json_skip['dividendYield']#grab dividend
json_marketCap = json_skip['marketCap']['fmt']#grab marketcap
json_volumeToday = json_skip['volume']['fmt']#grab today volume
json_fiftyTwoWeekHigh = json_skip['fiftyTwoWeekHigh']['fmt']#grab 52 week high
json_fiftyTwoWeekLow = json_skip['fiftyTwoWeekLow']['fmt']#grab 52 week low
try:
    json_pe = json_skip['trailingPE']['fmt']#grab pe ratio
except KeyError:
    json_pe = "-"#if no pe 

#if dividend exist grab fmt format of dividend else make dividend 0%
if json_yield != {}:
  json_yield = json_yield['fmt']
else:
  json_yield = "0%"

os.system("cls")

table = [['Mkt cap',json_marketCap],['P/E ratio',json_pe],['Div yield',json_yield],['Volume',json_volumeToday],['52-wk high',json_fiftyTwoWeekHigh],['52-wk low',json_fiftyTwoWeekLow]]#data to be displayed
print(tabulate(table,tablefmt="fancy_grid"))#tabulate and display data

#function that is passively called by matplotlib and removes interpolation alloying weekends and afterhours to be ingnored and remove data out of range. also labels x-axis based off of time range
def format_date(x, pos=None):
  ind = int(np.round(x))#convert tick position value to time index (tick 1 = index 1 in time list)
  if ind >= len(date_time) or ind < 0:#if invalid tick position ignore
    return '' 

  #change labels on x axis
  if time == "max" or time == "5y":
    return date_time[ind].strftime('%Y-%m')
  elif time == "1y" or time == "ytd" or time == "6mo" or time == "1mo":
    return date_time[ind].strftime('%m/%d')
  else:
    return date_time[ind].strftime('%H:%M')

#this chunk of code it to plot the graph, style, size, title, labels, displays graph, etc
plt.style.use('ggplot')#style
rcParams['figure.figsize'] = 8,8#size of grapg
fig, ax = plt.subplots()#subploating 
ax.xaxis.set_major_formatter(format_date)#formating data using function
plt.plot(np.arange(len(x)),y)#plot
plt.title(ticker)#title
plt.xlabel("time")#x title
plt.ylabel("price")#y title
plt.xticks(rotation=45)#rotate x axis markings
plt.show()#display plot