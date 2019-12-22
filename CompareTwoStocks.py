%matplotlib notebook
import pandas as pd
pd.core.common.is_list_like= pd.api.types.is_list_like
import pandas_datareader.data as web
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sqlalchemy import create_engine 


def compareTwoStocks():
    global stock1symbol
    global stock2symbol
    stock1symbol=input("enter first stock symbol(example: AMZN)") 
    stock2symbol=input("enter second stock symbol(example: AAPL)")
    global startTime
    global stopTime
    startTime=[int(x) for x in input("maximum interval for analysis is six months,enter the start time: year moth date(example: 2008 6 1)",).split()] 
    stopTime=[int(x) for x in input("enter the end time,: year moth date(example: 2009 3 31)",).split()]

    startDate=datetime.datetime(*startTime)
    endDate=datetime.datetime(*stopTime)
   
    stock1Data = getPriceHistory(stock1symbol,startDate,endDate)
    stock2Data = getPriceHistory(stock2symbol,startDate,endDate)

        
    saveStockDataToSqlite(stock1Data,stock2Data)
    
    printPValueAndPearsonsCorrelation(stock1Data,stock2Data)
    
    printMinimumAndMaximumValues()
    
    compareTwoStocksWithMatplotlib(stock1Data, stock2Data)

    
def saveStockDataToSqlite(stock1Data,stock2Data):
    global engine5
    engine5 = create_engine('sqlite:///stock_web_data.db')
    global stock1TableName
    global stock2TableName
    stock1TableName=stock1symbol+str(startTime+stopTime).strip("[]").replace(",","").replace(" ","_")
    stock2TableName=stock2symbol+str(startTime+stopTime).strip("[]").replace(",","").replace(" ","_")
    stock1Data[["AdjClose","percent_of_first_value","Volume"]].to_sql(
        name=stock1TableName,
        con=engine5,
        index=True,
    )
    stock2Data[["AdjClose","percent_of_first_value","Volume"]].to_sql(
        name=stock2TableName,
        con=engine5,
        index=True,
    )
    
def getPriceHistory(stock_symbol,startDate,endDate):
    stockPriceData = web.DataReader(stock_symbol, 'quandl', startDate, endDate) #use quandl, yahoo and google API's do not work
    stockPriceData.reset_index(inplace=True)
    stockPriceData.set_index("Date", inplace=True)
    stockPriceData["percent_of_first_value"]=stockPriceData["AdjClose"]/stockPriceData.iloc[-1]["AdjClose"]
    return stockPriceData 

def printPValueAndPearsonsCorrelation(stock1Data,stock2Data):
    x1,x2=pearsonr(list(stock1Data.AdjClose),list(stock2Data.AdjClose))
    print("Pearson's correlation coefficient for",stock1symbol,"and",stock2symbol,  "is",x1 ,",and the 2-tailed p-value is", x2 )

def printMinimumAndMaximumValues(): 
    df1 = pd.read_sql_query('select min(percent_of_first_value),Date from '+stock1TableName,engine5)
    df2 = pd.read_sql_query('select min(percent_of_first_value),Date from '+stock2TableName,engine5)
    print("the minimum value for {} was {}% of its starting valueand it was reached on {}".format(stock1symbol,round(list(df1.iloc[0])[0],2),list(df1.iloc[0])[1].split()[0]))
    print("the minimum value for {} was {}% of its starting valueand it was reached on {}".format(stock2symbol,round(list(df2.iloc[0])[0],2),list(df2.iloc[0])[1].split()[0]))

def compareTwoStocksWithMatplotlib(stock1Data, stock2Data):
    fig=plt.figure()
    ax1=plt.subplot2grid((8,1),(0,0),rowspan=4, colspan=1)
    plt.ylabel('% of starting price',fontsize=12)
    plt.xticks(rotation='30')
    ax1.plot(stock2Data.index, stock2Data.percent_of_first_value,linewidth=2,label=stock2symbol,color="red")
    ax1.plot(stock1Data.index, stock1Data.percent_of_first_value,linewidth=2,label=stock1symbol,color="green")
    plt.legend()

    ax2=plt.subplot2grid((8,1),(6,0),rowspan=2, colspan=1)
    plt.xlabel('Date')
    plt.ylabel('Volume(USD million)',fontsize=12)
    plt.xticks(rotation='30',fontsize=14)
    ax2.plot(stock2Data.index, stock2Data.Volume/1000000,linewidth=2,color="red")
    ax2.plot(stock1Data.index, stock1Data.Volume/1000000,linewidth=2,color="green")
    plt.show()


if __name__ == "__main__":
    compareTwoStocks()
