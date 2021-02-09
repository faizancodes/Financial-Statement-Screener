#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import csv
from itertools import cycle
from statistics import mean 
import random
from random import randint
import numpy as np
import time
from datetime import date


# In[7]:


symbols = []
companyNames = []
companySectors = []
userAgentList = []

useragents = open("useragents.txt", "r")

for line in useragents:
    userAgentList.append(line.replace('\n', ''))
    

delays = []

for x in range(100):
    delays.append(randint(50, 250) / 100)


# In[8]:


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


# In[9]:


def clean(stng):
    
    output = ''

    for letter in stng:
        if letter != '[' and letter != ']' and letter != "'": #and letter != ' ':
            output += letter
        
    return output


def cleanName(stng):
    
    output = stng.lower()
    
    stopwords = [' corporation', ' inc.', ' company', ' plc', '.com', ' co.', ' l.p.', ' ltd', ' corp.', ' limited' ' &amp;', ' ltd.']
    
    for word in stopwords:
        output = output.replace(word, '')
    
    output = output.replace(' ', '-')
    
    return output


def appendGrowth(lst):
    
    output = []
    
    for x in range(len(lst) - 1):
        
        try:
            diff = lst[x] - lst[x + 1]
            
            if diff > 0:
                output.append(round((lst[x] - lst[x + 1]) / abs(lst[x + 1]) * 100, 2))
            else:
                output.append(round((lst[x] - lst[x + 1]) / lst[x + 1] * 100, 2))
                
        except:
            continue
            
    return output



def getAvg(lst):
    
    summ = 0
    nums = 0
    
    for num in lst:
        if num != 0.0:
            summ += num
            nums += 1
    
    try:
        return round(summ / nums, 2)
    except:
        return 0 
    
    
    
def getSymbolsCSV(fileName):
    
    global symbols
    global companyNames
    
    print('\nLoading data from ' + fileName)

    with open(fileName) as csvfile:
    
        readCSV = csv.reader(csvfile, delimiter=',')
        
        for row in readCSV:
            
            symbol  = str(row[0]).replace('ï»¿', '')
            
            symbols.append(symbol)  
                
            companyNames.append(cleanName(row[1]))
            companySectors.append(row[2])
                

def exportData(fileName):

    MyFile = open(fileName, 'w')

    header = 'Symbol, Company Name, Sector, Score, AvgYearlyRevGrowth, NetGrowth, AvgGrossMarginGrowth, AvgNetIncGrowth, AvgNetIncMarginGrowth' + '\n'

    MyFile.write(header)

    for row in overall:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + fileName)


# In[10]:


#fileName = 'C:\\Users\\faiza\\Automated-Fundamental-Analysis\\SymbolData\\S&P500Symbols.csv'
#fileName = 'SymbolData\\SmallCapUnder2BSymbols.csv'
#getSymbolsCSV(fileName)


# In[11]:


overall = []

def getIncomeStatementScore(sym, ind):
    
    url = 'https://www.macrotrends.net/stocks/charts/' + sym + '/' + companyNames[ind] + '/financial-statements'
    print(url)
    
    agent = random.choice(userAgentList)
    headers = {'User-Agent': agent}
    pageError = False
    
    yearlyRevenues = []
    yearlyCogs = []
    yearlyNetIncome = []
    
    
    try:
        page = requests.get(url, headers=headers, proxies = {"http": next(proxyPool)})
        soup = str(BeautifulSoup(page.text, 'html.parser'))
    except:
        pageError = True
    
    if pageError == False:
    
        table = soup[soup.find('var originalData') : soup.find('localdata: originalData,')]
        table = table.split('","')


        startCogs = False
        endCogs = False
        startNetIncome = False
        endNetIncome = False


        for line in table:

            num = line[line.find('":"') + 3 : ]
            appended = False


            if '"field_name":"' in line:
                num = line[line.find(':"') + 2 : line.find('"}')]


            validCheck = len(num) != 0 and len(num) < 60 and num != '-'


            if startCogs == False and validCheck == True and appended == False:

                try:
                    yearlyRevenues.append(float(num))
                    appended = True
                except:
                    continue

            if 'cost-goods-sold' in line:
                startCogs = True


            if endCogs == False and startCogs == True and validCheck == True and appended == False:

                try:
                    yearlyCogs.append(float(num))
                    appended = True
                except:
                    continue


            if 'gross-profit' in line:
                endCogs = True

            if 'net-income' in line:
                startNetIncome = True

            if endNetIncome == False and startNetIncome == True and validCheck == True and appended == False:

                try:
                    yearlyNetIncome.append(float(num))
                    appended = True
                except:
                    continue

            if 'ebitda' in line:
                endNetIncome = True


        yearlyRevenues = yearlyRevenues[:4]
        yearlyCogs = yearlyCogs[:4]
        yearlyNetIncome = yearlyNetIncome[:4]

    
    if len(yearlyCogs) > 0 and len(yearlyRevenues) == len(yearlyCogs):
        
        print(sym + '\n')
        print('Yearly Revenues:', yearlyRevenues)
        print('Yearly Cogs:', yearlyCogs)
        print('Yearly Net Income:', yearlyNetIncome)
        print()


        grossMargins = []
        netMargins = []

        
        try:
            
            for x in range(len(yearlyRevenues)):
                grossMargins.append(round(((yearlyRevenues[x] - yearlyCogs[x]) / yearlyRevenues[x] * 100), 2))

            for x in range(len(yearlyRevenues)):
                netMargins.append(round((yearlyNetIncome[x] / yearlyRevenues[x] * 100), 2))



            yearlyRevGrowth = appendGrowth(yearlyRevenues)
            yearlyCogsGrowth = appendGrowth(yearlyCogs)
            yearlyNetIncGrowth = appendGrowth(yearlyNetIncome)
            yearlyGrossMarginGrowth = appendGrowth(grossMargins)
            yearlyNetIncMarginGrowth = appendGrowth(netMargins)

            avgYearlyRevGrowth = getAvg(yearlyRevGrowth)
            avgYearlyCogsGrowth = getAvg(yearlyCogsGrowth)
            avgNetIncGrowth = getAvg(yearlyNetIncGrowth)
            avgGrossMarginGrowth = getAvg(yearlyGrossMarginGrowth)
            avgNetIncMarginGrowth = getAvg(yearlyNetIncMarginGrowth)

            netGrowth = round(avgYearlyRevGrowth - avgYearlyCogsGrowth, 2)


            print('Yearly Rev Growth:', yearlyRevGrowth, avgYearlyRevGrowth)
            print('Yearly Cogs Growth:', yearlyCogsGrowth, avgYearlyCogsGrowth)
            print('Yearly Net Inc Growth:', yearlyNetIncGrowth, avgNetIncGrowth)

            print('\nGross Margins:', grossMargins, getAvg(grossMargins))
            print('Yearly Gross Margin Growth:', yearlyGrossMarginGrowth, avgGrossMarginGrowth)

            print('\nNet Margins:', netMargins, getAvg(netMargins))
            print('Yearly Net Margin Growth:', yearlyNetIncMarginGrowth, avgNetIncMarginGrowth)

            print('\nNet Growth', netGrowth)

            score = round(((avgYearlyRevGrowth * 20) + (netGrowth * 20) + (avgGrossMarginGrowth * 10) + (avgNetIncGrowth + avgNetIncMarginGrowth) / 10), 2)

            overall.append([sym, companyNames[ind], companySectors[ind], score, avgYearlyRevGrowth, netGrowth, avgGrossMarginGrowth, avgNetIncGrowth, avgNetIncMarginGrowth])


            print('\nFinal Score:', score)
            print()
            
        except:
            print('Err:', sym)


# In[12]:

symbolSet = 'SmallCapUnder2BSymbols'
fileName = 'SymbolData\\' + symbolSet + '.csv'
getSymbolsCSV(fileName)


for i, stock in enumerate(symbols):
    getIncomeStatementScore(stock, i)
   

today = date.today()
d = today.strftime("%m/%d/%y")


saveToFilename = symbolSet + '_IncStatementRatings_' + str(d).replace('/', '.') + '.csv'
exportData(saveToFilename)


