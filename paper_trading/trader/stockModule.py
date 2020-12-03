import requests
import json
import xlsxwriter
import pandas as pd
import os
import yfinance as yf
import yahoo_fin.stock_info
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px


class Stock:
    API_KEY = "bv4403v48v6tcp17fv10"

    def __init__(self, ticker):
        self.ticker = ticker
        self.tickerName = ticker.info["symbol"]

    def __str__(self):
        return self.ticker.info["shortName"]

    def getAnnualFinancialsReported(self):
        r = requests.get(
            'https://finnhub.io/api/v1/stock/financials-reported?symbol='+tickerName+'&token='+API_KEY)
        return r.json()

    def getCompanyProfile(self):
        r = requests.get(
            'https://finnhub.io/api/v1/stock/profile2?symbol=AAPL&token=bv4403v48v6tcp17fv10')
        return r.json()

    def getPlotlyPriceHistory(self, tickerName, price, period="1d", interval="5m"):

        priceDF = self.ticker.history(period=period, interval=interval)
        priceDF["DatetimeCol"] = priceDF.index
        #fig = go.Figure([go.Line(x=priceDF["DatetimeCol"], y=priceDF['Close'])])

        data = go.Line(x=priceDF["DatetimeCol"], y=priceDF['Close'])
        layout = go.Layout(
            title=period,

            titlefont=dict(

                #family="Courier New, monospace",
                size=30,
                color="#7f7f7f"
            ),
            margin=dict(l=0, r=0, t=0.1, b=0),
            plot_bgcolor="#FFFFFF"

        )

        fig = go.Figure(
            data=data,
            layout=layout
        )
        fig.update_layout(
            font_family="Arial",
            font_color="blue",
            title={
                'text': period,
                "y": 1,
                "x": 0.5},


        )
        '''
        fig.update_layout(
            title=str(tickerName) + "<br>$" + str(price) +"<br><br>",
            title_x=0.04,
            title_y=0.93,
            titlefont=dict(
                #family="Courier New, monospace",
                size=30,
                color="#7f7f7f"
                ),
            margin=dict(l=0, r=0, t=00, b=0),
        )
        '''
        plt_div = plot(fig, output_type='div')

        return plt_div

    @classmethod
    def getPositionValue(cls, positionsJSON):
        value = 0
        for positionKey in positionsJSON.keys():
            if (positionKey == "name"):
                continue
            value += yahoo_fin.stock_info.get_live_price(
                positionKey) * positionsJSON[positionKey]
        return value

    def getStockSummary(self):

        stockInfo = self.ticker.info
        summaryKeys = set(["previousClose", "regularMarketOpen", "twoHundredDayAverage",
                           "fiftyDayAverage", "open", "beta", "currency", "volume",
                           "trailingPE", "forwardPE", "exchange", "shortName",
                           "profitMargins", "52WeekChange", "shortRatio", "volume",
                           "fiftyTwoWeekHigh", "enterpriseToEbitda", "marketCap", "volume",
                           "city", "industry", "currency"])
        newDict = {}
        for i in stockInfo.keys():

            if (i in summaryKeys):
                newDict[i] = stockInfo[i]
        newDict["longBusinessSummary"] = self.ticker.info["longBusinessSummary"]
        return newDict
