import enum
from datetime import datetime
from dateutil import parser
import time
import lxml
from lxml import html
import requests
import pandas as pd
import re
#from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class Sections(enum.Enum):
    Summary = 1
    Chart = 2
    Conversation = 3
    Statistics = 4
    Historical = 5
    Profile = 6
    Financial = 7
    Analysis = 8
    Options = 9
    Holders = 10
    Sustainability = 11
    BalanceSheet = 12
    CashFlow = 13

class clickableValues(enum.Enum):
    Quarterly = 1
    ExpandAll = 2
    

class FinanceScraper:


    _baseurl = 'https://finance.yahoo.com/quote/'
    #https://query1.finance.yahoo.com/v8/
    _urlP = '?p='
    _summarySection = ''
    _chartSection = '/chart'
    _conversationSection = '/community'
    _statisticsSection = '/key-statistics'
    _historicalDataSection = '/history'
    _profileSection = '/profile'
    _financialsSection = '/financials'
    _balanceSheetSection = '/balance-sheet'
    _cashFlowSection = '/cash-flow'
    _analysisSection = '/analysis'
    _optionsSection = '/options'
    _holdersSection = '/holders'
    _sustainabilitySection = '/sustainability'

    _headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    _chromedriver = r'C:\ChromeDriver\chromedriver.exe'

    def __init__(self, symbol, db = None ):
        self._ticker = symbol

    def manipulateWebpage(self, url, value: int):
        options = Options()
        options.add_argument("--headless")

        browser = webdriver.Chrome(executable_path=self._chromedriver, options=options)
        browser.get(url)
        time.sleep(3)

        if value == clickableValues.Quarterly:
            lt = browser.find_element_by_xpath("//section/div[1]/div[2]/button/div")
            lt.click()
            lt =  browser.find_element_by_xpath("//section/div[2]/button/div")
            lt.click()
        elif value == clickableValues.ExpandAll:
            lt =  browser.find_element_by_xpath("//section/div[2]/button/div")
            lt.click()
        else:
            raise NotImplementedError

        return browser.page_source

    def expandNumber(self, val):
        if val.find(',') > 0:
            val = val.replace(',','')

        if val.find('M') > 0:
            val = val.replace('M','')
            val = float(val) * 1000000
        elif val.find('B') > 0:
            val = val.replace('B','')
            val = float(val) * 1000000000
        elif val.find('T') > 0:
            val = val.replace('T','')
            val = float(val) * 1000000000000
        elif val.find('k') > 0:
            val = val.replace('k','')
            val = float(val) * 1000
        else:
            float(val)

        return val

    def buildUrl(self, s: int  ):
        url = self._baseurl + self._ticker 
        if s == Sections.Summary.value:
            url += self._urlP + self._ticker
        elif s == Sections.Analysis.value:
            url += self._analysisSection + self._urlP + self._ticker
        elif s == Sections.Chart.value:
            url += self._chartSection + self._urlP + self._ticker
        elif s == Sections.Conversation.value:
            url += self._conversationSection + self._urlP + self._ticker
        elif s == Sections.Financial.value:
            url += self._financialsSection + self._urlP + self._ticker
        elif s == Sections.BalanceSheet.value:
            url += self._balanceSheetSection + self._urlP + self._ticker
        elif s == Sections.CashFlow.value:
            url += self._cashFlowSection + self._urlP + self._ticker
        elif s == Sections.Historical.value:
            url += self._historicalDataSection + self._urlP + self._ticker
        elif s == Sections.Holders.value:
            url += self._holdersSection + self._urlP + self._ticker
        elif s == Sections.Options.value:
            url += self._optionsSection + self._urlP + self._ticker
        elif s == Sections.Profile.value:
            url += self._profileSection + self._urlP + self._ticker
        elif s == Sections.Statistics.value:
            url += self._statisticsSection + self._urlP + self._ticker
        elif s == Sections.Sustainability.value:
            url += self._sustainabilitySection + self._urlP + self._ticker
        else:
            raise NotImplementedError
    
        return url
    
    def getAllData(self):
        self.getSummaryData()
        self.getStatisticsData()
        self.getFinancialData()

    def getSummaryData(self):
        page = requests.get(self.buildUrl(Sections.Summary.value), self._headers)
        xmlpage = html.fromstring(page.content)
        parsed_rows = []
        
        # valuation measures
        table_rows = xmlpage.xpath("//tr[contains(@class, 'Bxz(bb)')]")
        #table_rows = xmlpage.xpath("//tr[contains(@class, 'D(itb')]")
        
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath("./td")
            for rs in sumval:
                val = rs.xpath('.//span/text()[1]')
                
                if len(val) < 1:
                    val2 = table_row.xpath("./td[contains(@class, 'Ta(end')]")
                    val3 = val2[0].text.split('-')
                    if len(val3)> 1:
                        parsed_row.append(val3[0].strip())
                        val = val3[1].strip()
                    else:
                        p = re.compile('(\d+\.\d+) \((\d+\.\d+)')
                        m =p.match(val2[0].text)
                        if m:
                            parsed_row.append(m.group(1))
                            val = m.group(2)
                        else:
                            parsed_row.append(None)
                            val = None

                        #val = val2[0].text

                parsed_row.append(val)

                            
            parsed_rows.append(parsed_row)

        self.statisticsFrame = pd.DataFrame(parsed_rows)

        #print(self.statisticsFrame)
        return 0


    def getAnalysisData(self):
        raise NotImplementedError
    def getChartData(self):
        raise NotImplementedError
    def getConversationData(self):
        raise NotImplementedError

    def getFinancialData(self):
        # 3 different urls to call income statement, balance sheet, cashflow
        page = self.manipulateWebpage(self.buildUrl(Sections.Financial.value), clickableValues.ExpandAll)

        #page = requests.get(self.buildUrl(Sections.Financial.value), self._headers)
        #xmlpage = html.fromstring(page.content)
        xmlpage = html.fromstring(page)

        parsed_rows = []
        
        # annual income statement column headings
        table_rows = xmlpage.xpath("//section/div[4]/div[1]/div[1]/div[1]/div")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./div')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                parsed_row.append(val)
    
            if (len(parsed_row) > 0):
                parsed_rows.append(parsed_row)

        #table_rows = xmlpage.xpath("//div[contains(@data-test, 'fin-row')]")
        #table_rows = xmlpage.xpath("//section/div[4]/div[1]/div[1]/div[2]/div")
        table_rows = xmlpage.xpath("//div[contains(@class, 'D(tbrg)')]")
        for table_row in table_rows:
            parsed_row = []
#            sumval = table_row.xpath("descendant::/div[contains(@data-test, 'fin-row')]")
            sumval = table_row.xpath("./div/div[contains(@class, 'D(tbr)')]")
            for rs in sumval:
                sumval2 = rs.xpath("descendant::div[contains(@class, 'D(tbc)')]")
                for rs2 in sumval2:
                    val = rs2.xpath(".//span/text()[1]")
                    parsed_row.append(val)
                if(len(parsed_row)>0):    
                    parsed_rows.append(parsed_row)

                while sumval3 := rs.xpath("following-sibling::div"): 
                    for rs3 in sumval3:
                        parsed_row=[]
                        sumval4 = rs3.xpath("./div/div/div[contains(@class, 'D(tbc)')]")
                        for rs4 in sumval4:
                            val = rs4.xpath(".//span/text()[1]")
                            parsed_row.append(val)
                        if(len(parsed_row) > 0):
                            parsed_rows.append(parsed_row)
                
                # sumval3 = rs.xpath("following-sibling::div")
                # for rs3 in sumval3:
                #     parsed_row=[]
                #     sumval4 = rs3.xpath("./div/div/div[contains(@class, 'D(tbc)')]")
                #     for rs4 in sumval4:
                #         val = rs4.xpath(".//span/text()[1]")
                #         parsed_row.append(val)
                #     if(len(parsed_row) > 0):
                #         parsed_rows.append(parsed_row)
            


        self.FinancialFrame = pd.DataFrame(parsed_rows)

        #print(self.statisticsFrame)
        return 0

    def getHistoricalData(self):
        raise NotImplementedError
    def getHoldersData(self):
        raise NotImplementedError
    def getOptionsData(self):
        raise NotImplementedError
    def getProfileData(self):
        raise NotImplementedError
    def getStatisticsData(self):
        
        page = requests.get(self.buildUrl(Sections.Statistics.value), self._headers)
        

        xmlpage = html.fromstring(page.content)
        
       
        parsed_rows = []
        
        # valuation Measures
        table_rows = xmlpage.xpath("//section/div[3]/div[1]/div[2]/div/div[1]/div[1]/table/thead/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./th')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
            parsed_rows.append(parsed_row)

        table_rows = xmlpage.xpath("//section/div[3]/div[1]/div[2]/div/div[1]/div[1]/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
            parsed_rows.append(parsed_row)

        self.StatisticsValuationFrame = pd.DataFrame(parsed_rows)
        
        
        # Trading Information
       
        parsed_rows = []
        
        # stock price history
        table_rows = xmlpage.xpath("//section/div[3]/div[2]/div/div[1]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
            parsed_rows.append(parsed_row)
               
        # share statistics
        table_rows = xmlpage.xpath("//section/div[3]/div[2]/div/div[2]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)


        # dividends & splits
        table_rows = xmlpage.xpath("//section/div[3]/div[2]/div/div[3]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)
        
        # Fiscal Year 
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[1]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        # Profitability 
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[2]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        # Management Effectiveness 
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[3]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        # Income statement
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[4]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        # Balance Sheet
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[5]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        # Cash Flow Statement
        table_rows = xmlpage.xpath("//section/div[3]/div[3]/div/div[6]/div/div/table/tbody/tr")
        for table_row in table_rows:
            parsed_row = []
            sumval = table_row.xpath('./td')
            for rs in sumval:
                val = rs.xpath(".//span/text()[1]")
                if len(val) < 1:
                     val2 = rs.xpath("./text()[1]")
                     val = val2
                
                parsed_row.append(val)
        
            parsed_rows.append(parsed_row)

        self.StatisticsTradingInformationFrame = pd.DataFrame(parsed_rows)

        return 0

    def getSustainabilityData(self):
        raise NotImplementedError

    def getBeta(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[0][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def get52WeekChange(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[1][1]
            for x in rc:
                rc = float(x.replace('%',''))
         

        return rc
    def getSP52WeekChange(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[2][1]
            for x in rc:
                rc = float(x.replace('%',''))
         

        return rc
    def get52WeekHigh(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[3][1]
            for x in rc:
                rc = float(x)
         

        return rc
    def get52WeekLow(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[4][1]
            for x in rc:
                rc = float(x)
         

        return rc
    def get50DayMovingAverage(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[5][1]
            for x in rc:
                rc = float(x)
         

        return rc
    def get200DayMovingAverage(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[6][1]
            for x in rc:
                rc = float(x)
         

        return rc
    def getAverageVolume3Months(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[7][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getAverageVolume10Day(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[8][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getSharesOutstanding(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[9][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getFloat(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[10][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getHeldByInsiders(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[11][1]
            for x in rc:
                rc = float(x.replace('%',''))
         
        return rc
    def getHeldByInstitutions(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[12][1]
            for x in rc:
                rc = float(x.replace('%',''))
         
        return rc
    def getSharesShort(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[13][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getShortRatio(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[14][1]
            for x in rc:
                rc = float(x)
 
        return rc   
    def getShortPercentFloat(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[15][1]
            for x in rc:
                rc = float(x.replace('%',''))
         
        return rc
    def getShortPercentOutstanding(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[16][1]
            for x in rc:
                rc = float(x.replace('%',''))
         
        return rc        
    def getSharesShortPriorMonth(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[17][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getForwardAnnualDividentRate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[18][1]
            for x in rc:
                try:
                    rc = float(x)
                except ValueError:
                    rc = 0
 
        return rc          
    def getForwardAnnualDividentYield(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[19][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getTrailingAnnualDividentRate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[20][1]
            for x in rc:
                try:
                    rc = float(x)
                except ValueError:
                    rc = 0
 
        return rc          
    def getTrailingAnnualDividentYield(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[21][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def get5YearAverageDividentYield(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[22][1]
            for x in rc:
                try:
                    rc = float(x)
                except ValueError:
                    rc = 0
 
        return rc 
    def getPayoutRatio(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[23][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getDividentDate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[24][1]
            for x in rc:
                try:
                    rc = parser.parse(x)
                except ValueError:
                    rc = 0

        return rc
    def getExDividentDate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[25][1]
            for x in rc:
                try:
                    rc = parser.parse(x)
                except ValueError:
                    rc = 0

        return rc
    def getLastSplitFactor(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[26][1]
 
        return rc
    def getLastSplitDate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[27][1]
            for x in rc:
                try:
                    rc = parser.parse(x)
                except ValueError:
                    rc = 0

        return rc
    def getFiscalYearEndsDate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[28][1]
            for x in rc:
                try:
                    rc = parser.parse(x)
                except ValueError:
                    rc = 0

        return rc
    def getMostRecentQuarterDate(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[29][1]
            for x in rc:
                try:
                    rc = parser.parse(x)
                except ValueError:
                    rc = 0

        return rc
    def getProfitMargin(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[30][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getOperatingMargin(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[31][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getReturnOnAssets(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[32][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getReturnOnEquity(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[33][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getRevenue(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[34][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getRevenuePerShare(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[34][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getQuarterlyRevenueGrowth(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[36][1]
            for x in rc:
                try:
                    rc = float(x.replace('%',''))
                except ValueError:
                    rc = 0

        return rc
    def getGrossProfits(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[37][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getEBITDA(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[38][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getNetIncomeAviToCommon(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[39][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc  
    def getDilutedEPS(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[40][1]
            for x in rc:
                rc = float(x)
 
        return rc 
    def getTotalDebt(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[44][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getCurrentRatio(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[46][1]
            for x in rc:
                rc = float(x)
 
        return rc   
    def getBookValuePerShare(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[47][1]
            for x in rc:
                rc = float(x)
 
        return rc          
    def getOperatingCashFlow(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[48][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getLeveredFreeCashFlow(self):
        rc = None

        if self.StatisticsTradingInformationFrame.empty:
            pass
        else:
            rc = self.StatisticsTradingInformationFrame.loc[49][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getMarketCapIntradayCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[1][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc    
    def getMarketCapIntradayArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[1][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc    
    def getEnterpriseValueCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[2][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getEnterpriseValueArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[2][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc    
    def getTrailingPECurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[3][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getTrailingPEArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[3][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc   
    def getForwardPECurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[4][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getForwardPEArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[4][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc   
    def getPEGRatioCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[5][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getPEGRatioArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[5][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc  
    def getPriceSalesCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[6][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getPriceSalesArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[6][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc     
    def getPriceBookCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[7][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getPriceBookArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[7][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc     
    def getEnterpriseValueRevenueCurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[8][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getEnterpriseValueRevenueArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[8][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc    
    def getEnterpriseValueEBITDACurrentQuarter(self):
        rc = None

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            rc = self.StatisticsValuationFrame.loc[9][1]
            for x in rc:
                x = self.expandNumber(x)
                rc = float(x)
 
        return rc 
    def getEnterpriseValueEBITDAArray(self):
        rc = []

        if self.StatisticsValuationFrame.empty:
            pass
        else:
            for i in range(1,6):
                for j in self.StatisticsValuationFrame.loc[9][i]:
                    j = self.expandNumber(j)
                    j = float(j)   
                    rc.append(j)


 
        return rc 

    def getPreviousClose(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[0][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def getOpen(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[1][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def getBid(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[2][1]
            for x in rc:
                rc = x #float(x)
 
        return rc
    def getAsk(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[3][1]
            for x in rc:
                rc = x #float(x)
 
        return rc
    def getDayRange(self):
        rc = []

        if self.statisticsFrame.empty:
            pass
        else:
            for i in range(1,3):
                j = self.expandNumber(self.statisticsFrame.loc[4][i])
                j = float(j)   
                rc.append(j)

        return rc    
    def get52WeekRange(self):
        rc = []

        if self.statisticsFrame.empty:
            pass
        else:
            for i in range(1,3):
                j = self.expandNumber(self.statisticsFrame.loc[5][i])
                j = float(j)   
                rc.append(j)

        return rc    
    def getVolume(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[6][1]
            for x in rc:
                rc = float(self.expandNumber(x))
 
        return rc
    def getAverageVolume(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[7][1]
            for x in rc:
                rc = float(self.expandNumber(x))
 
        return rc
    def getMarketCap(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[8][1]
            for x in rc:
                j = self.expandNumber(x)
                rc = float(j)
 
        return rc
    def getBeta5YMonthly(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[9][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def getPERatioTTM(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[10][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def getEPSTTM(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[11][1]
            for x in rc:
                rc = float(x)
 
        return rc
    def getEarningsDate(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[12][1]
            #for x in rc:
            #    rc = float(x)
 
        return rc
    def getForwardDividentYield(self):
        rc = []

        if self.statisticsFrame.empty:
            pass
        else:
                for i in range(1,3):
                    j = self.expandNumber(self.statisticsFrame.loc[13][i])
                    j = float(j)   
                    rc.append(j)
 
        return rc
    def getExDividendDate(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[14][1]
            #for x in rc:
            #    rc = float(x)
 
        return rc
    def get1YearTargetEst(self):
        rc = None

        if self.statisticsFrame.empty:
            pass
        else:
            rc = self.statisticsFrame.loc[15][1]
            for x in rc:
                rc = float(x)
 
        return rc       
def test():
    try:
        
        f = FinanceScraper('KO')
        #s = Sections()
        print(f.buildUrl(1))
        print(f.buildUrl(2))
        print(f.buildUrl(3))
        print(f.buildUrl(4))
        print(f.buildUrl(5))
        print(f.buildUrl(6))
        print(f.buildUrl(7))
        print(f.buildUrl(8))
        print(f.buildUrl(9))
        print(f.buildUrl(10))
        print(f.buildUrl(11))
        print(f.buildUrl(12))
        print(f.buildUrl(13))
        f.getAllData()
        print (f.getBeta())        
        print (f.get52WeekChange())
        print (f.getSP52WeekChange())
        print (f.get52WeekHigh())
        print (f.get52WeekLow())
        print (f.get50DayMovingAverage())
        print (f.get200DayMovingAverage())
        print (f.getAverageVolume3Months())
        print (f.getAverageVolume10Day())
        print (f.getSharesOutstanding())
        print (f.getFloat())
        print (f.getHeldByInsiders())
        print (f.getHeldByInstitutions())
        print (f.getSharesShort())
        print (f.getShortRatio())
        print (f.getShortPercentFloat())
        print (f.getShortPercentOutstanding())
        print (f.getSharesShortPriorMonth())
        print (f.getForwardAnnualDividentRate())
        print (f.getForwardAnnualDividentYield())
        print (f.getTrailingAnnualDividentRate())
        print (f.getTrailingAnnualDividentYield())
        print (f.get5YearAverageDividentYield())
        print (f.getPayoutRatio())
        print (f.getDividentDate())
        print (f.getExDividentDate())
        print (f.getLastSplitFactor())
        print (f.getLastSplitDate())
        print (f.getFiscalYearEndsDate())
        print (f.getMostRecentQuarterDate())
        print (f.getProfitMargin())
        print (f.getOperatingMargin())
        print (f.getReturnOnAssets())
        print (f.getReturnOnEquity())
        print (f.getRevenue())
        print (f.getRevenuePerShare())
        print (f.getQuarterlyRevenueGrowth())
        print (f.getGrossProfits())
        print (f.getEBITDA())
        print (f.getNetIncomeAviToCommon())
        print (f.getDilutedEPS())
        print (f.getTotalDebt())
        print (f.getCurrentRatio())
        print (f.getBookValuePerShare())
        print (f.getOperatingCashFlow())
        print (f.getLeveredFreeCashFlow())
        print (f.getMarketCapIntradayCurrentQuarter())
        print (f.getMarketCapIntradayArray())
        print (f.getEnterpriseValueCurrentQuarter())
        print (f.getEnterpriseValueArray())
        print (f.getTrailingPECurrentQuarter())
        print (f.getTrailingPEArray())
        print (f.getForwardPECurrentQuarter())
        print (f.getForwardPEArray())
        print (f.getPEGRatioCurrentQuarter())
        print (f.getPEGRatioArray())
        print (f.getPriceSalesCurrentQuarter())
        print (f.getPriceSalesArray())
        print (f.getPriceBookCurrentQuarter())
        print (f.getPriceBookArray())
        print (f.getEnterpriseValueRevenueCurrentQuarter())
        print (f.getEnterpriseValueRevenueArray())
        print (f.getEnterpriseValueEBITDACurrentQuarter())
        print (f.getEnterpriseValueEBITDAArray())
        print (f.getPreviousClose())
        print (f.getOpen())
        print (f.getBid())
        print (f.getAsk())
        print (f.getDayRange())
        print (f.get52WeekRange())
        print (f.getVolume())
        print (f.getAverageVolume())
        print (f.getMarketCap())
        print (f.getBeta5YMonthly())
        print (f.getPERatioTTM())
        print (f.getEPSTTM())
        print (f.getEarningsDate())
        print (f.getForwardDividentYield())
        print (f.getExDividendDate())
        print (f.get1YearTargetEst())

        # testing pandas stuff
        #print(f.StatisticsTradingInformationFrame.head())
        #print(f.statisticsFrame.head())
        

       # print(f.StatisticsTradingInformationFrame.tail())
        #print(f.StatisticsTradingInformationFrame.describe())

 
        #  dtypes    - data types
        #  amzn = amzn.replace({'\$':''}, regex = True)  get rid of $
        #  # Renaming column names and converting the data types
        # df = amzn 
        # df.columns = ['Date', 'Close', 'Volume', 'Open', 'High', 'Low'] 
        # Converting data types
        # df = df.astype({"Close": float, "Volume": int, "Open": float, "High": float, "Low": float}) 
        # df.dtypes
        #
        #
        #print(f.summaryFrame)
        #print(f.StatisticsValuationFrame)
        #print(f.StatisticsTradingInformationFrame)
        #print(f.getEnterpriseValueArray())
        #print(f.getEnterpriseValueEBITDAArray())
        #print(f.getForwardPEArray())
        #print(f.getTrailingPEArray())
        #print(f.getPEGRatioArray())
        #print(f.getPriceSalesArray())
        #print(f.getPriceBookArray())
        
        

        

    except Exception as e:
        print(f'had exception : {e}')
    



if __name__ == "__main__": test()      


