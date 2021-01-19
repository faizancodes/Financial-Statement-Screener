#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
from itertools import cycle
from csv import reader
import seaborn as sns
import numpy as np
import statistics
import ast
import sys
import time
import os
import csv


# In[23]:


def getProxies(inURL):
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 

proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)


# In[24]:


agent = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


def clean(stng):
    
    output = ''

    for letter in stng:
        if letter != '[' and letter != ']' and letter != "'": #and letter != ' ':
            output += letter
        
    return output


# In[25]:


symbolSets = ['S&P500', 'MidCap', 'SmallCapOver300', 'SmallCapUnder2B']

for i, symbolSet in enumerate(symbolSets):
    
    print('\nGetting ' + symbolSet + ' Symbols...')
    
    if i == 0: 
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=idx_sp500'
    elif i == 1:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_midover'
    elif i == 2:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_smallover'
    else:
        rawURL = 'https://finviz.com/screener.ashx?v=111&f=cap_smallunder'
        
        
    symbols = []
    companyNames = []
    companySectors = []
    pageCounter = 1
    stocksAdded = 20
    
    
    while stocksAdded == 20:

        stocksAdded = 0
        
        URL = rawURL + '&r=' + str(pageCounter)
        page = requests.get(URL, headers=agent, proxies = {"http": next(proxyPool)})
        soup = BeautifulSoup(page.content, 'html.parser')

        tableLightStocks = soup.find_all('tr', {'class': 'table-light-row-cp'})
        tableDarkStocks = soup.find_all('tr', {'class': 'table-dark-row-cp'})

        tableStocks = list(tableLightStocks) + list(tableDarkStocks)

        for result in tableStocks:

            result = str(result)
            rawSymbol = result[result.find('"quote.ashx?t=') + 5 : result.find('"quote.ashx?t=') + 25]
            symbol = rawSymbol[rawSymbol.find('=') + 1 : rawSymbol.find('&')]
            
            rawCompanyName = result[result.find("src='https://charts2.finviz.com") + 85 : result.find("src='https://charts2.finviz.com") + 170]
            companyName = rawCompanyName[rawCompanyName.find('t;') + 2 : rawCompanyName.find('&lt')]
            
            rawCompanySector = result[result.find("src='https://charts2.finviz.com") + 525 : result.find("src='https://charts2.finviz.com") + 720]
            sector = rawCompanySector[rawCompanySector.find(';b=1">') + 6 : rawCompanySector.find('</a></td><td')]
            
            #print(symbol, companyName, sector)
            #print()
            
            companyNames.append(companyName.replace(',', ''))
            companySectors.append(sector)

            symbols.append(symbol)
            stocksAdded += 1
        
            
        pageCounter += 20


# In[26]:



MyFile = open('SymbolData\\' + symbolSet + 'Symbols.csv', 'w')

for i, row in enumerate(symbols):
    MyFile.write(clean(str(row)) + ',' + clean(companyNames[i]) + ',' + clean(companySectors[i]))
    MyFile.write('\n')

MyFile.close()
print('Saved as ' + 'SymbolData\\' + symbolSet + 'Symbols.csv')


# In[ ]:





# In[ ]:




