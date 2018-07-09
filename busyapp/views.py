from django.shortcuts import render
from django.http import HttpResponse
import requests

from .forms import OnTheGoForm, PlannerForm, TouristForm
from .ml import predictor_svm
from .ml import predictor_regression
from .ml import predictor_ann
from .ml import predictor_ann_improved
from .ml import getWeather

from busy.settings import STATIC_ROOT

import random
import datetime

# Create your views here.
def index(request):
    return render(request, 'index.html')


def onthego(request):
    return render(request, 'onthego.html')


def theplanner(request):
    return render(request, 'theplanner.html')


def tourist(request):
    return render(request, 'tourist.html')

def busStops(request):
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/busstopinformation?format=json&operator=bac")
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)

    #if the above API fails, try another...
    r = requests.get("https://data.smartdublin.ie/cgi-bin/rtpi/busstopinformation?format=json&operator=bac")
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)
    else: #If all APIs fail, use local file
        with open(STATIC_ROOT+'/bus_data/busstopinformation.json', 'r', encoding="utf8") as file:
            return HttpResponse(file.read())

def busStopAutosuggest(request):
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/busstopinformation")
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)

def testView(request):
    return HttpResponse("Hi!")


def onthegoform(request):
    if request.method == 'GET':
        form = OnTheGoForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busNum = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']

            #Automatically get current time of day
            now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
            time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

            #call the machine learning function & parse the returned seconds into hours, minutes & seconds.
            journeyTime = {'h' : 0, 'm' : 0, 's' : 0}
            #journeyTimeSeconds = predictor_ann(busNum, fromVar, toVar, time_of_day, weatherCode=getWeather())

            weekDay = {'mon':0, 'tue':1, 'wed':0, 'thu':0, 'fri':0, 'sat':0, 'sun':0} #testing...
            dayOfYear = 0.6

            journeyTimeSeconds = predictor_ann_improved(busNum,int(fromVar)/95,int(toVar)/95,time_of_day/86400,int(getWeather())/804,0,0,0,0,0,0,dayOfYear,weekDay)

            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s']) #get rid of trailing floating point for seconds.

            # some random numbers for TESTING
            cost = getWeather() #TESTING weather value in place of cost for now...
            bestStartTime = datetime.datetime.now() + datetime.timedelta(minutes=60) #note 1h addition for linux servers

            # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'onthego.html', {'busNum' : busNum,
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    #'journeyTime' : journeyTime,
                                                    'journeyTime' : journeyTimeSeconds,
                                                    'cost' : cost,
                                                    'bestStartTime' : bestStartTime})
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")


def plannerform(request):
    if request.method == 'GET':
        form = PlannerForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busVar = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            whenVar = form.cleaned_data['when_var']

            return HttpResponse("Bus Num: "+busVar+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"When: "+whenVar) #FOR DEBUGGING
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")


def touristform(request):
    if request.method == 'GET':
        form = TouristForm(request.GET)

        #Example of reading unvalidated form data. This may crash the app.
        #print(form['busnum'].value())
        #print(form.data['busnum'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busVar = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            whenVar = form.cleaned_data['when_var']

            return HttpResponse("Bus Num: "+busVar+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"When: "+whenVar) #FOR DEBUGGING
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")