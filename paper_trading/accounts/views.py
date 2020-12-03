from django.shortcuts import render
from django.template import RequestContext

# Create your views here.
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from trader.models import Trader
from django.contrib.auth.decorators import login_required
import json
from dataclasses import dataclass
from yahoo_fin.stock_info import get_live_price
from django.http import HttpResponse
from trader.stockModule import Stock
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import logout
from plotly.offline import plot
import plotly.graph_objs as go
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("FSD")
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login/')
        else:
            print("ERROR")
            messages.error(request, 'Invalid information.')

    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def portfolio(request):
    CurrentTrader = Trader.objects.get(user=request.user)
    positionsDict = (json.loads(
        str(CurrentTrader.positions).replace("'", '"')))
    CurrentTrader.AUM = round(Stock.getPositionValue(
        positionsDict) + float(CurrentTrader.cash), 3)
    StockArray = []

    for i in positionsDict.keys():
        if i == "name":
            continue
        stockPrice = get_live_price(i)

        positionInfo = {
            'ticker': i,
            'count': positionsDict[i],
            'price': round(stockPrice, 3),
            'value': round(stockPrice * positionsDict[i], 3),

        }

        StockArray.append(positionInfo)

    context = {"User": request.user,
               "CurrentTrader": CurrentTrader,
               "PositionsArray": StockArray
               }

    return render(request, 'portfolio.html', context)


@login_required
def logout_user(request):
    logout(request)


@login_required
def account_settings(request):

    context = {}
    return render(request, "account_settings.html", context)


@login_required
def change_info(request):

    if request.method == "POST":
        currentUser = request.user
        currentUser.username = request.POST.get("username")
        currentUser.first_name = request.POST.get('first_name')
        currentUser.last_name = request.POST.get("last_name")
        currentUser.email = request.POST.get("email")
        currentUser.save()
        return redirect("/accounts/account_settings/")
    else:
        return HttpResponse("BAD!")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
