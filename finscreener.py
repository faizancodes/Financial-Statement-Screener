import requests
from bs4 import BeautifulSoup
import csv

symbols = []
stockCounter = 0
c = 0


def getSymbols(inURL):
    
    global symbols
    global stockCounter
    global c
    global stocksToAnalyze
    global searchThrough

    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    symbs = soup.find_all('a', {'class' : 'screener-link-primary'})

    for x in range(len(symbs)):
        if '&amp;b=1' in str(symbs[x]):
            symbols.append(str(symbs[x])[str(symbs[x]).find('&amp;b=1') + 10 : str(symbs[x]).find('/a') - 1])
            stockCounter = stockCounter + 1

        if stockCounter % 20 == 0:
            c = c + 20
            getSymbols(searchThrough + '&r=' + str(c))
        
        if stockCounter >= stocksToAnalyze:
            break


def getSymbolsCSV():
    
    global symbols

    with open('C:\\Users\\faiza\\OneDrive\\Desktop\\StockData\\SymbolData\\S&P500Symbols.csv') as csvfile:
    
        readCSV = csv.reader(csvfile, delimiter=',')
        
        for row in readCSV:
            if row[0] =='ï»¿A':
                symbols.append('A')
            else:
                symbols.append(row[0])

        
def bubbleSort(subList): 
    
    l = len(subList) 

    for i in range(0, l): 
        
        for j in range(0, l-i-1): 
            
            if (subList[j][1] < subList[j + 1][1]): 
                tempo = subList[j] 
                subList[j]= subList[j + 1] 
                subList[j + 1] = tempo 

    return subList 


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

proxies = {
  'http': 'http://' + pxs[0],
  'http': 'http://' + pxs[1],
  'http': 'http://' + pxs[2],
  'http': 'http://' + pxs[3],
  'http': 'http://' + pxs[4],
  'http': 'http://' + pxs[5],
  'http': 'http://' + pxs[6],
  'http': 'http://' + pxs[7],
  'http': 'http://' + pxs[8],
  'http': 'http://' + pxs[9],
  'http': 'http://' + pxs[10],
  'http': 'http://' + pxs[11],
}

allStocksRevGrowth = []
allStocksNetGrowth = []
allStocksCombGrowth = []

allStocksCashGrowth = []

def convertNum(stng):
    output = ''
    for c in stng:
        if c.isdigit() or c == '.' or c == '-':
            output += c

    try:
        return float(output)
    except:
        return 0


def convertString(stng):
    output = ''
    for c in stng:
        if c.isalpha():
            output += c

    try:
        return output
    except:
        return 0


def getIncomeStatement(sym):
    
    global proxies
    global allStocksRevGrowth
    global allStocksNetGrowth
    global allStocksCombGrowth
    
    sym = convertString(sym)
 
    inURL = 'https://quotes.wsj.com/' + sym + '/financials/annual/income-statement'

    page = requests.get(inURL, proxies=proxies)
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    insertIntoCOGS = False

    yearlyRevenues = []
    yearlyCOGS = []
    yearlyNetIncome = []

    yearlyRevGrowth = []
    yearlyCOGSGrowth = []
    yearlyNetIncomeGrowth = []

    #print(soup + '\n\n\n')
    
    rawRevenues = soup[soup.find('Sales/Revenue') + 20 : soup.find('<td class="data_smallgraph">')]
    rawRevGrowth = soup[soup.find('Sales Growth') : soup.find('Sales Growth') + 250]
    
    rawCOGS = soup[soup.find('Cost of Goods Sold (COGS)') + 45 : soup.find('Cost of Goods Sold (COGS)') + 300]
    rawCOGSGrowth = soup[soup.find('COGS Growth') : soup.find('COGS Growth') + 250]
    
    rawNetIncome = soup[soup.find('Net Income') + 25 : soup.find('Net Income') + 300]
    rawNetIncomeGrowth = soup[soup.find('Net Income Growth') : soup.find('Net Income Growth') + 250]


    if 'data-region="na,us"' in rawCOGS:
        
        if len(rawRevenues) > 1000:
            rawRevenues = soup[soup.find('Interest Income') + 20 : soup.find('<td class="data_smallgraph">')]
            rawCOGS = soup[soup.find('Total Interest Expense') + 30 : soup.find('Total Interest Expense') + 350]

            rawRevGrowth = soup[soup.find('Interest Income Growth') + 30 : soup.find('Interest Income Growth') + 350]
            rawCOGSGrowth = soup[soup.find('Total Interest Expense Growth') + 25 : soup.find('Total Interest Expense Growth') + 250]

        if 'Losses, Claims &amp; Reserves' in soup:
            rawCOGS = soup[soup.find('Losses, Claims &amp; Reserves') + 40 : soup.find('Losses, Claims &amp; Reserves') + 350]
            rawCOGSGrowth = soup[soup.find('Losses, Claims &amp; Reserves Growth') + 40 : soup.find('Losses, Claims &amp; Reserves Growth') + 350]
                
        elif 'Total Expense' in soup:
            rawCOGS = soup[soup.find('Total Expense') + 20 : soup.find('Total Expense') + 350]
            insertIntoCOGS = True


    if '<td class="">-</td> <td class="">-</td> <td class="">-</td> <td class="">-</td> <td class="">-</td>' in rawCOGS:
         
        if 'SG&amp;A Expense' in soup:
            rawCOGS = soup[soup.find('SG&amp;A Expense') + 20 : soup.find('SG&amp;A Expense') + 350]
            rawCOGSGrowth = soup[soup.find('SGA Growth') + 10 : soup.find('SGA Growth') + 350]


    for x in range(5):
        
        yearlyRevenues.append(convertNum(rawRevenues[rawRevenues.find('"">') + 3 : rawRevenues.find('</td>')]))
        rawRevenues = rawRevenues[rawRevenues.find('</td>') + 1 : ]
        
        yearlyNetIncome.append(convertNum(rawNetIncome[rawNetIncome.find('"">') + 3 : rawNetIncome.find('</td>')]))
        rawNetIncome = rawNetIncome[rawNetIncome.find('</td>') + 1 : ]

        yearlyCOGS.append(convertNum(rawCOGS[rawCOGS.find('"">') + 3 : rawCOGS.find('</td>')]))
        rawCOGS = rawCOGS[rawCOGS.find('</td>') + 1 : ]

    for x in range(4):

        yearlyRevGrowth.append(convertNum(rawRevGrowth[rawRevGrowth.find('e">') : rawRevGrowth.find('%')]))
        rawRevGrowth = rawRevGrowth[rawRevGrowth.find('%') + 1 : ]

        if insertIntoCOGS == False:
            yearlyCOGSGrowth.append(convertNum(rawCOGSGrowth[rawCOGSGrowth.find('e">') : rawCOGSGrowth.find('%')]))
            rawCOGSGrowth = rawCOGSGrowth[rawCOGSGrowth.find('%') + 1 : ]

        yearlyNetIncomeGrowth.append(convertNum(rawNetIncomeGrowth[rawNetIncomeGrowth.find('e">') : rawNetIncomeGrowth.find('%')]))
        rawNetIncomeGrowth = rawNetIncomeGrowth[rawNetIncomeGrowth.find('%') + 1 : ]


    if insertIntoCOGS == True:
        for x in range(len(yearlyCOGS) - 1):
            yearlyCOGSGrowth.append(round(((yearlyCOGS[x] - yearlyCOGS[x + 1]) / yearlyCOGS[x + 1]) * 100, 3))


    if 0 in yearlyCOGS:
        print('****************************' + sym)
        print(yearlyRevenues)
        print(yearlyCOGS)
    
    else:
        print()
        print(sym)
        print('Yearly Revenues:', yearlyRevenues)
        print('Yearly COGS:', yearlyCOGS)
        print('Yearly Net Income:', yearlyNetIncome)
        print('Yearly Revenue Growth(%):', yearlyRevGrowth)
        print('Yearly COGS Growth(%):', yearlyCOGSGrowth)
        print('Yearly Net Income Growth(%):', yearlyNetIncomeGrowth)

      
    avgRevGrowth = 0
    avgCOGSGrowth = 0
    avgNetIncGrowth = 0
    
    netGrowth = 0

    yRevGrowth = 0
    yCOGSGrowth = 0
    yNetIncGrowth = 0

    revLen = 0
    cogsLen = 0
    netIncLen = 0


    for num in yearlyRevGrowth:
        
        if num != 0:
            yRevGrowth += num
            revLen += 1

    for num in yearlyCOGSGrowth:

        if num < 0:
            yCOGSGrowth += abs(num)
            cogsLen += 1

        elif num != 0:
            yCOGSGrowth += num
            cogsLen += 1

    for num in yearlyNetIncomeGrowth:
        
        if num != 0:
            yNetIncGrowth += num
            netIncLen += 1


    if revLen != 0 and cogsLen != 0 and netIncLen != 0:

        avgRevGrowth = yRevGrowth / revLen
        avgCOGSGrowth = yCOGSGrowth / cogsLen
        avgNetIncGrowth = yNetIncGrowth / netIncLen

    netGrowth = avgRevGrowth - avgCOGSGrowth
    allStocksNetGrowth.append([sym, netGrowth])

    combGrowth = ((netGrowth * 5) + avgNetIncGrowth) / 2
    allStocksCombGrowth.append([sym, combGrowth, netGrowth, avgRevGrowth, avgCOGSGrowth, avgNetIncGrowth])

    print('Net Growth:', netGrowth)
    print('Comb Growth:', combGrowth)
    print('Avg Rev Growth:', avgRevGrowth)
    print('Avg COGS Growth:', avgCOGSGrowth)
    print()



def getBalanceSheet(sym):

    global allStocksCashGrowth

    sym = convertString(sym)
 
    inURL = 'https://quotes.wsj.com/' + sym + '/financials/annual/balance-sheet'

    page = requests.get(inURL, proxies=proxies)
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    yearlyCashSTInv = [] 
    yearlycashSTInvGrowth = []

    yearlyTotalAssets = []
    yearlyTotalAssetsGrowth = []

    yearlyTotalLiabilities = []
    yearlyTotalLiabilitiesGrowth = []

    rawCashSTInv = soup[soup.find('Cash &amp; Short Term Investments') + 40 : soup.find('Cash &amp; Short Term Investments') + 250]
    rawCashSTInvGrowth = soup[soup.find('Cash &amp; Short Term Investments Growth') + 45 : soup.find('Cash &amp; Short Term Investments Growth') + 250]

    rawTotalAssets = soup[soup.find('Total Assets FOR CALCULATION PURPOSES') + 50 : soup.find('Total Assets FOR CALCULATION PURPOSES') + 250]
    rawTotalAssetsGrowth = soup[soup.find('Assets - Total - Growth') + 30 : soup.find('Assets - Total - Growth') + 250]

    rawTotalLiabilities =  soup[soup.find('Total Liabilities') + 25 : soup.find('Total Liabilities') + 250]

    #print(soup)
    #print(rawTotalAssets)
    #print()
    #print(rawTotalAssetsGrowth)
    #print(rawTotalLiabilities)


    if 'data-region="na,us">' in rawCashSTInv:

        if 'Total Cash &amp; Due from Banks' in soup:
            rawCashSTInv = soup[soup.find('Total Cash &amp; Due from Banks') + 40 : soup.find('Total Cash &amp; Due from Banks') + 250]
            rawCashSTInvGrowth = soup[soup.find('Cash &amp; Due from Banks Growth') + 40 : soup.find('Cash &amp; Due from Banks Growth') + 250]

        elif 'Cash Only' in soup:
            rawCashSTInv = soup[soup.find('Cash Only') + 20 : soup.find('Cash Only') + 250]
            rawCashSTInvGrowth = soup[soup.find('Cash Growth') + 20 : soup.find('Cash Growth') + 250]

    
    if 'data-region="na,us">' in rawTotalAssetsGrowth:
        
        if 'Total Assets Growth' in soup:
            rawTotalAssetsGrowth = soup[soup.find('Total Assets Growth') + 30 : soup.find('Total Assets Growth') + 250]

        if 'Assets - Total - 1 Year Growth' in soup:
            rawTotalAssetsGrowth = soup[soup.find('Assets - Total - 1 Year Growth') + 30 : soup.find('Assets - Total - 1 Year Growth') + 250]

        if 'Assets - Total Growth' in soup:
            rawTotalAssetsGrowth = soup[soup.find('Assets - Total Growth') + 30 : soup.find('Assets - Total Growth') + 250]
    
    for x in range(5):

        yearlyCashSTInv.append(convertNum(rawCashSTInv[rawCashSTInv.find('"">') + 3 : rawCashSTInv.find('</td>')]))        
        rawCashSTInv = rawCashSTInv[rawCashSTInv.find('</td>') + 1 : ]

        yearlyTotalAssets.append(convertNum(rawTotalAssets[rawTotalAssets.find('"">') + 3 : rawTotalAssets.find('</td>')]))        
        rawTotalAssets = rawTotalAssets[rawTotalAssets.find('</td>') + 1 : ]

        yearlyTotalLiabilities.append(convertNum(rawTotalLiabilities[rawTotalLiabilities.find('"">') + 3 : rawTotalLiabilities.find('</td>')]))        
        rawTotalLiabilities = rawTotalLiabilities[rawTotalLiabilities.find('</td>') + 1 : ]

    for x in range(4):

        yearlycashSTInvGrowth.append(convertNum(rawCashSTInvGrowth[rawCashSTInvGrowth.find('e">') : rawCashSTInvGrowth.find('%')]))
        rawCashSTInvGrowth = rawCashSTInvGrowth[rawCashSTInvGrowth.find('%') + 1 : ]
    
        yearlyTotalAssetsGrowth.append(convertNum(rawTotalAssetsGrowth[rawTotalAssetsGrowth.find('e">') : rawTotalAssetsGrowth.find('%')]))
        rawTotalAssetsGrowth = rawTotalAssetsGrowth[rawTotalAssetsGrowth.find('%') + 1 : ]


    for x in range(len(yearlyTotalLiabilities) - 1):
        try:
            yearlyTotalLiabilitiesGrowth.append(round(((yearlyTotalLiabilities[x] - yearlyTotalLiabilities[x + 1]) / yearlyTotalLiabilities[x + 1]) * 100, 3))
        except:
            yearlyTotalLiabilitiesGrowth.append(0)


    avgCashSTInvGrowth = 0
    yCashSTInvGrowth = 0
    cashSTInvLen = 0

    avgAssetsGrowth = 0
    yTotalAssetsGrowth = 0
    totalAssetsLen = 0 

    avgLiabilitiesGrowth = 0
    yTotalLiabilitiesGrowth = 0
    totalLiabilitiesLen = 0

    for num in yearlycashSTInvGrowth:
        
        if num != 0:
            yCashSTInvGrowth += num
            cashSTInvLen += 1

    for num in yearlyTotalAssetsGrowth:

        if num != 0:
            yTotalAssetsGrowth += num
            totalAssetsLen += 1

    for num in yearlyTotalLiabilitiesGrowth:

        if num != 0:
            yTotalLiabilitiesGrowth += num
            totalLiabilitiesLen += 1


    if cashSTInvLen != 0 and totalAssetsLen != 0 and totalLiabilitiesLen != 0:
        avgCashSTInvGrowth = yCashSTInvGrowth / cashSTInvLen
        avgAssetsGrowth = yTotalAssetsGrowth / totalAssetsLen
        avgLiabilitiesGrowth = yTotalLiabilitiesGrowth / totalLiabilitiesLen

    combStat = ((((avgAssetsGrowth - avgLiabilitiesGrowth) * 5)) + avgCashSTInvGrowth) / 2

    print(sym)
    #print('CashStInv', yearlyCashSTInv)
    print('CashStInv Growth', yearlycashSTInvGrowth)
    print('Avg CashStInv Growth', avgCashSTInvGrowth)
    #print('Total Assets', yearlyTotalAssets)
    print('Total Assets Growth', yearlyTotalAssetsGrowth)
    print('Avg Assets Growth', avgAssetsGrowth)
    #print('Total Liabilities', yearlyTotalLiabilities)
    print('Liabilities Growth', yearlyTotalLiabilitiesGrowth)
    print('Avg Liabilities Growth', avgLiabilitiesGrowth)
    print(combStat)
    print()

    allStocksCashGrowth.append([sym, combStat])



def writeToCSV(lst, name):

    with open('C:\\Users\\faiza\\OneDrive\\Desktop\\StockData\\Finscreener Outputs\\' + name + '.csv', 'w') as f:

        f.write('Symbol, Comb Growth, Net Growth, Avg Rev Growth, Avg COGS Growth, Avg Net Inc Growth' + '\n')

        for x in range(len(lst)):
            f.write(lst[x][0] + ',' + str(lst[x][1]) + ',' + str(lst[x][2]) + ',' + str(lst[x][3]) + ',' + str(lst[x][4]) + ',' + str(lst[x][5]) + '\n')

    print('Saved as ' + name + '.csv')


sAndP = 'https://finviz.com/screener.ashx?v=111&f=idx_sp500'
midCap = 'https://finviz.com/screener.ashx?v=111&f=cap_mid'

basicMaterials = 'https://finviz.com/screener.ashx?v=111&f=sec_basicmaterials'
conglomerates = 'https://finviz.com/screener.ashx?v=111&f=sec_conglomerates'
comsumerGoods = 'https://finviz.com/screener.ashx?v=111&f=sec_consumergoods'
financials = 'https://finviz.com/screener.ashx?v=111&f=sec_financial'
healthcare = 'https://finviz.com/screener.ashx?v=111&f=sec_healthcare'
industrialGoods = 'https://finviz.com/screener.ashx?v=111&f=sec_industrialgoods'
services = 'https://finviz.com/screener.ashx?v=111&f=sec_services'
tech = 'https://finviz.com/screener.ashx?v=111&f=sec_technology'
utilities = 'https://finviz.com/screener.ashx?v=111&f=sec_utilities'

allStocks = 'https://finviz.com/screener.ashx?v=111'

searchThrough = sAndP
stocksToAnalyze = 30


#getSymbols(searchThrough)
getSymbolsCSV()


'''
for stock in symbols:
    getIncomeStatement(stock)
'''


for stock in symbols:
    getBalanceSheet(stock)
    print()


#getBalanceSheet('O')

bubbleSort(allStocksNetGrowth)
bubbleSort(allStocksCombGrowth)
bubbleSort(allStocksCashGrowth)

for x in range(len(allStocksCashGrowth)):
    print(allStocksCashGrowth[x][0], allStocksCashGrowth[x][1])


#writeToCSV(allStocksCombGrowth, 'CombStatsOutput')
