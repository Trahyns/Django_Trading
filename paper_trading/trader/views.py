from django.shortcuts import render
from django.shortcuts import render
from .models import Trader
import json
from .stockModule import Stock
from django.contrib.auth.decorators import login_required
from yahoo_fin.stock_info import get_live_price, get_data
import yfinance as yf
from django.http import HttpResponse
from plotly.offline import plot
import plotly.graph_objs as go
from django.http import HttpResponseRedirect
from accounts.views import portfolio
from django.shortcuts import redirect
from django.contrib import messages

# Create your views here.


def home_view(request):
    if request.user.is_authenticated:
        return redirect('/accounts/portfolio/')
    return render(request, "home.html")


@login_required
def leaderboard_list_view(request):
    trader_objects = Trader.objects.all()

    for trader in trader_objects:
        positionsDict = (json.loads(str(trader.positions).replace("'", '"')))
        trader.AUM = Stock.getPositionValue(positionsDict) + float(trader.cash)
        trader.save()

    trader_objects = Trader.objects.order_by('-AUM')

    context = {
        "trader_objects": trader_objects,
        "ranks": range(0, len(trader_objects))
    }

    return render(request, "trader_leaderboards.html", context)


@login_required
def sell(request):
    CurrentTrader = Trader.objects.get(user=request.user)

    positionsDict = (json.loads(
        str(CurrentTrader.positions).replace("'", '"')))
    CurrentTrader.AUM = Stock.getPositionValue(
        positionsDict) + float(CurrentTrader.cash)
    if request.method == "POST":
        ShareCount = int(request.POST.get('ShareCount', None))
        TickerName = str(request.POST.get('TickerName'))
        print(request.POST)
        Price = get_live_price(TickerName)
        if (ShareCount > positionsDict[TickerName]):
            messages.add_message(request, messages.INFO,
                                 'Too many stocks being sold')
            return HttpResponseRedirect("/accounts/portfolio/")

        CurrentTrader.cash = CurrentTrader.cash + (ShareCount * Price)
        if (TickerName in positionsDict.keys()):
            positionsDict[TickerName] = positionsDict[TickerName] - ShareCount
            if (positionsDict[TickerName] == 0):
                del positionsDict[TickerName]
            CurrentTrader.positions = positionsDict

        else:
            messages.add_message(request, messages.INFO,
                                 'Do not own this stock')

            return HttpResponse("/accounts/portfolio")

        CurrentTrader.AUM = Stock.getPositionValue(
            positionsDict) + float(CurrentTrader.cash)
        CurrentTrader.save()
        return HttpResponseRedirect('/accounts/portfolio/')
    else:
        return HttpResponse("Purchase failed")


@login_required
def buy(request):
    CurrentTrader = Trader.objects.get(user=request.user)

    positionsDict = (json.loads(
        str(CurrentTrader.positions).replace("'", '"')))
    CurrentTrader.AUM = Stock.getPositionValue(
        positionsDict) + float(CurrentTrader.cash)
    if request.method == "POST":
        ShareCount = int(request.POST.get('ShareCount', None))
        TickerName = str(request.POST.get('TickerName')).upper()
        Price = get_live_price(TickerName)
        if (CurrentTrader.cash < ShareCount * Price):
            return HttpResponse("Not enough cash")

        CurrentTrader.cash = CurrentTrader.cash - (ShareCount * Price)
        if (TickerName in positionsDict.keys()):
            positionsDict[TickerName] = positionsDict[TickerName] + ShareCount
            CurrentTrader.positions = positionsDict
        else:
            positionsDict[TickerName] = ShareCount
            CurrentTrader.positions = positionsDict

        CurrentTrader.AUM = Stock.getPositionValue(
            positionsDict) + float(CurrentTrader.cash)

        CurrentTrader.save()
        return HttpResponseRedirect('/accounts/portfolio/')
    else:
        return HttpResponse("Purchase failed")


@login_required
def index(request):
    return render(request, 'ticker.html')


@login_required
def search(request):
    if request.method == 'POST':

        try:
            tickerName = request.POST.get('ticker', None).upper()
            graphTime = request.POST.get("graphTime", None)

            graphConfigurations = [
                ("1d", "1m"),
                ("5d", "15m"),
                ("1mo", "1h"),
                ("3mo", "1d"),
                ("1y", "1d"),
                ("5y", "1wk"),
                ("max", "1mo"),
            ]

            get_data(tickerName)
            stock = Stock(yf.Ticker(tickerName))
            price = round(get_live_price(tickerName), 3)

            Summary = stock.getStockSummary()
            titleName = Summary["shortName"] + "(" + tickerName + ")"

            if graphTime is not None:
                graphTime = int(graphTime)
                plt = stock.getPlotlyPriceHistory(titleName, price,
                                                  period=graphConfigurations[graphTime][0], interval=graphConfigurations[graphTime][1])
            else:
                plt = stock.getPlotlyPriceHistory(
                    titleName, price, period="1d", interval="1m")

            #user = Person.objects.get(name = search_id)
            #do something with user
            #html = ("<H1>%s</H1>", user)
            context = {
                "TickerName": tickerName,
                "Price": price,
                "Summary": Summary,
                "Profile": stock.getCompanyProfile,
                "StockPlot": plt

            }
            return render(request, "search.html", context)
        except AssertionError:
            return HttpResponse("no such stock")
    else:
        return render(request, 'form.html')
