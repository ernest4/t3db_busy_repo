from django.shortcuts import render
from django.http import HttpResponse
import requests
import numpy as np
import os
import datetime
import pytz

from .forms import OnTheGoForm, PlannerForm, TouristForm
from .ml import predictor_ann_improved
from .ml import getWeather
from .ml import getDayOfYear
from .ml import secondsSinceMidnight
from .ml import getWeekDayBinaryArray
from .ml import getWeather
from .ml import getModelAndProgNum

from busy.settings import STATIC_ROOT

# Create your views here.
def index(request):
    return render(request, 'index.html')


def onthego(request):
    return render(request, 'onthego.html')


def theplanner(request):
    return render(request, 'theplanner.html')


def tourist(request):
    return render(request, 'tourist.html')

def accessibility(request):
    return render(request, 'accessibility.html')

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

#function to return Google Directions API query results for the map
def directions(request):
    params = request.GET;
    r = requests.get("https://maps.googleapis.com/maps/api/directions/json",
                     params={'origin': params['origin'],
                             'destination': params['destination'],
                             'mode': params['mode'],
                             'transit_mode': params['transit_mode'],
                             'key': os.environ.get('DIRECTIONS_API')})
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)

#function to return RTPI query results for Bus Stop Autosuggests
def busStopAutosuggest(request):
    params = request.GET;
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/busstopinformation",
                     params={'format': params['format'],
                             'operator': params['operator'],
                             'stopname': params['stopname']})
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)
    else:
        return HttpResponse("format=" + params['format']+ ", operator=" + params['operator']+ ", stopname=" + params['stopname'])

#function to return RTPI query results for Bus Routes Autosuggests
def busRoutesAutosuggest(request):
    params = request.GET;
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/routelistinformation",
                     params={'format': params['format'],
                             'operator': params['operator']})
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)
    else:
        return HttpResponse("format=" + params['format']+ ", operator=" + params['operator'])
    
#Function for RTPI querying for Route Number Autosuggests.
def routeNumberAutosuggest(request):
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/routelistinformation")
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)

def loadTest(request):
    with open(STATIC_ROOT+'/load_testing/loaderio-e39f002a9fff5739d5e13b22d4f09b69.txt', 'r', encoding="utf8") as file:
        return HttpResponse(file.read())

def testView(request):
    #r = request.GET;
    #return render(request, 'testpage.html', {'msg1' : r['t']})
    return render(request, 'testpage.html')


def personas(request):
    return render(request, "personas.html")

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

            time_of_day = secondsSinceMidnight()
            weather = getWeather()
            dayOfYear = getDayOfYear()
            weekDay = getWeekDayBinaryArray()

            # Fetch the right model
            ann_improved, start_stop, end_stop = getModelAndProgNum(busNum, fromVar, toVar)

            if ann_improved is None:  # Model could not be retreived
                # server side rendering - replace with AJAX for client side rendering in the future
                errorMSG = "Oops something went wrong :/"
                errorMSG2 = "The combination of route and stops you have entered may not be valid \
                            and/or may not be in service on this particular weekday."
                errorMSG3 = "Please check your inputs and try again."
                return render(request, 'onthego.html', {'busNum': busNum,
                                                        'from': fromVar,
                                                        'to': toVar,
                                                        'journeyTime': errorMSG,
                                                        'cost': errorMSG2,
                                                        'bestStartTime': errorMSG3,
                                                        'error': 1}) #Error code > 0 means something bad happened...


            # call the machine learning function & parse the returned seconds into hours, minutes & seconds.
            journeyTimeSeconds = predictor_ann_improved(ann_improved=ann_improved,
                                                        start_stop=start_stop,
                                                        end_stop=end_stop,
                                                        time_of_day=time_of_day,
                                                        weatherCode=weather,
                                                        secondary_school=0,
                                                        primary_school=0,
                                                        trinity=0,
                                                        ucd=0,
                                                        bank_holiday=0,
                                                        event=0,
                                                        day_of_year=dayOfYear,
                                                        weekday=weekDay,
                                                        delay=0) #0 FOR TESTING

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
                                                    #'cost' : cost,
                                                    #'bestStartTime' : bestStartTime})
                                                    'cost': start_stop, #FOR DEBUGGING
                                                    'bestStartTime': end_stop, #FOR DBUGGING
                                                    'error': 0}) #0 means everything good
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")




def plannerform(request):
    if request.method == 'GET':
        form = PlannerForm(request.GET)

        # Example of reading unvalidated form data. This may crash the app.
        # print(form['busnum_var'].value())
        # print(form.data['busnum_var'])

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busNum = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            dateVar = form.cleaned_data['date_var']
            timeVar = form.cleaned_data['time_var']

            time_of_day = datetime.datetime(1970, 1, 1, timeVar.hour, timeVar.minute, timeVar.second, tzinfo=datetime.timezone.utc).timestamp()
            weather = getWeather() #TESTING, CREATE getFutureWeather() FUNCTION IN THE FUTURE....
            dayOfYear = (datetime.datetime(dateVar.year, dateVar.month, dateVar.day, tzinfo=datetime.timezone.utc)
                       - datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)).total_seconds()
            weekDay = getWeekDayBinaryArray(datetime.datetime(dateVar.year, dateVar.month, dateVar.day, tzinfo=datetime.timezone.utc).weekday())


            # Fetch the right model
            ann_improved, start_stop, end_stop = getModelAndProgNum(busNum, fromVar, toVar, weekdayIndex=datetime.datetime.today().weekday())

            if ann_improved is None:  # Model could not be retreived
                # server side rendering - replace with AJAX for client side rendering in the future
                errorMSG = "Oops something went wrong :/"
                errorMSG2 = "The combination of route and stops you have entered may not be valid \
                            and/or may not be in service on this particular weekday."
                errorMSG3 = "Please check your inputs and try again."
                return render(request, 'theplanner.html', {'busNum': busNum,
                                                            'from': fromVar,
                                                            'to': toVar,
                                                            'journeyTime': errorMSG,
                                                            'cost': errorMSG2,
                                                            'bestStartTime': errorMSG3,
                                                            'error': 1}) #Error code > 0 means something bad happened...

            # call the machine learning function & parse the returned seconds into hours, minutes & seconds.
            journeyTimeSeconds = predictor_ann_improved(ann_improved=ann_improved,
                                                        start_stop=start_stop,
                                                        end_stop=end_stop,
                                                        time_of_day=time_of_day,
                                                        weatherCode=weather,
                                                        secondary_school=0,
                                                        primary_school=0,
                                                        trinity=0,
                                                        ucd=0,
                                                        bank_holiday=0,
                                                        event=0,
                                                        day_of_year=dayOfYear,
                                                        weekday=weekDay,
                                                        delay=0)  # 0 FOR TESTING

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s'])  # get rid of trailing floating point for seconds.

            # some random numbers for TESTING
            cost = 2.85  # TESTING for now...
            bestStartTime = datetime.datetime.now() + datetime.timedelta(
                minutes=60)  # note 1h addition for linux servers

            # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'theplanner.html', {'busNum': busNum,
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime': journeyTime,
                                                    # 'cost' : cost,
                                                    # 'bestStartTime' : bestStartTime})
                                                    'cost': start_stop,  # FOR DEBUGGING
                                                    'bestStartTime': end_stop,  # FOR DBUGGING
                                                    'error': 0})  # 0 means everything good


            #return HttpResponse("Bus Num: "+busNum+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"Date: "+str(dateVar)+"<br>"+"Time: "+str(timeVar)) #FOR DEBUGGING

        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")


def bestTime(request):
    if request.method == 'GET':
        form = PlannerForm(request.GET)

        # Example of reading unvalidated form data. This may crash the app.
        # print(form['busnum_var'].value())
        # print(form.data['busnum_var'])

        # Prefered way of handling forms, validate first before using.
        if form.is_valid():
            busVar = form.cleaned_data['busnum_var']
            fromVar = form.cleaned_data['from_var']
            toVar = form.cleaned_data['to_var']
            busDirect = form.cleaned_data['bus_direction']
            timeVar = form.cleaned_data['time_var']
            dateVar = form.cleaned_data['date_var']


            #time_var = time_var.to_datetime...
            time_var = 0 #ONLY FOR TESTING
            rolling_time = time_var - 3600

            min_time = np.inf
            for i in range(13):
                prediction = 0 #ONLY FOR TESTING
                trip_time = prediction

                if trip_time < min_time:
                    min_time = trip_time

                rolling_time += 600

            return min_time

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
