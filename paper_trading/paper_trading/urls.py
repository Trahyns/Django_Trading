"""paper_trading URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.shortcuts import redirect

from accounts import views as core_views
from django.contrib import admin
from django.urls import path
from trader.views import leaderboard_list_view, index, search, buy, sell, home_view
from accounts.views import portfolio, signup, logout_user, change_password, account_settings, change_info
urlpatterns = [
    path('admin/', admin.site.urls),
    path('leaderboard/', leaderboard_list_view),
    url(r'^signup/$', core_views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/portfolio/', portfolio),
    path('index/', index),
    path('search/', search),
    path('accounts/buy/', buy),
    path('accounts/sell/', sell),
    path('accounts/signup/', signup),
    path('accounts/logout/', logout_user),
    path('accounts/account_settings/', account_settings),
    path('accounts/change_password/', change_password),
    path('accounts/change_info/', change_info),
    path('home/', home_view),
    path("", home_view)
]
