from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.views.decorators.csrf import requires_csrf_token
from data import loaders

def loadUsers(request):
    if not request.user.is_superuser:
    	return HttpResponse("Invalid login")
    	
    minUserNumber = int(request.GET.get('minusernumber', 1))
    maxUserNumber = int(request.GET.get('maxusernumber', 1000))
    loaders.ConstituentReader.loadUsers(minUserNumber, maxUserNumber)
    return HttpResponse("loadUsers(%s, %s)\n" % (minUserNumber, maxUserNumber))

def loadInterests(request):
    if not request.user.is_superuser:
    	return HttpResponse("Invalid login")
    	
    minUserNumber = int(request.GET.get('minusernumber', 1))
    maxUserNumber = int(request.GET.get('maxusernumber', 1000))
    numInterests = int(request.GET.get('count', 1))
    
    with open('exception.log', 'a') as log:
        log.write("loadInterests(%s, %s, %s)\n" % (minUserNumber, maxUserNumber, numInterests))
        log.flush()
    loaders.ConstituentReader.loadinterests(minUserNumber, maxUserNumber, numInterests)
    return HttpResponse("loadInterests(%s, %s, %s)\n" % (minUserNumber, maxUserNumber, numInterests))