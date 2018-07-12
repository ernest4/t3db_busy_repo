from django.shortcuts import render
from django.http import HttpResponse
import requests

from .forms import OnTheGoForm, PlannerForm, TouristForm
from .ml import predictor_svm
from .ml import predictor_regression
from .ml import predictor_ann
from .ml import predictor_ann_improved
from .ml import getWeather
from .ml import getNormalizedDayOfYear
from .ml import secondsSinceMidnight
from .ml import getWeekDayBinaryArray
from .ml import getNormalizedWeather
from .ml import secondsNormalizedSinceMidnight

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

def loadTest(request):
    with open(STATIC_ROOT+'/load_testing/loaderio-e39f002a9fff5739d5e13b22d4f09b69.txt', 'r', encoding="utf8") as file:
        return HttpResponse(file.read())

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

            #normalize the input data
            busNum = busNum
            fromVarNorm = float(fromVar)/59
            toVarNorm = float(toVar)/59

            time_of_day = secondsNormalizedSinceMidnight()
            weather = getNormalizedWeather()
            dayOfYear = getNormalizedDayOfYear()
            weekDay = getWeekDayBinaryArray()

            # call the machine learning function & parse the returned seconds into hours, minutes & seconds.
            journeyTimeSeconds = predictor_ann_improved(busNum=busNum,
                                                        start_stop=fromVarNorm,
                                                        end_stop=toVarNorm,
                                                        time_of_day=time_of_day,
                                                        weatherCode=weather,
                                                        secondary_school=0,
                                                        primary_school=0,
                                                        trinity=0,
                                                        ucd=0,
                                                        bank_holiday=0,
                                                        event=0,
                                                        day_of_year=dayOfYear,
                                                        weekday=weekDay)

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s']) #get rid of trailing floating point for seconds.

            # some random numbers for TESTING
            cost = 2.85 #TESTING for now...
            bestStartTime = datetime.datetime.now() + datetime.timedelta(minutes=60) #note 1h addition for linux servers

            # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'onthego.html', {'busNum' : busNum,
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime' : journeyTime,
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