from django.shortcuts import render
from django.http import HttpResponse
import requests
import numpy as np
import os
import datetime
import pytz
import csv
import json

from .forms import OnTheGoForm, PlannerForm, TouristForm
from .ml import predictor_ann_improved
from .ml import getWeather
from .ml import getDayOfYear
from .ml import secondsSinceMidnight
from .ml import getWeekDayBinaryArray
from .ml import getWeather
from .ml import getModelAndProgNum

from busy.settings import STATIC_ROOT

# Create dictionary object for events from csv file

with open(STATIC_ROOT+'/model_info/events18.csv', mode='r') as infile:
    reader = csv.reader(infile)
    events = {rows[0]:[rows[1],rows[2],rows[3],rows[4],rows[5],rows[6]] for rows in reader}

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

# Function to get the events of a certain day
def getEvents(date):
    pass
#"""

# RTPI request based on route and stop_id
# If there are buses coming, returns list of tuples with arrival time and the delay
def getLiveBusInfo(stop_id, route_id):
    times=[]
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?"
                     "stopid="+stop_id+"&routeid="+route_id+"&maxresults&operator&format=json")
    if r.status_code == requests.codes.ok:
        data = json.loads(r.content.decode('utf-8'))
        if len(data['results']) > 0:
            i = 0
            while i < 3 and i<len(data['results']):
                timeArr = data['results'][i]['arrivaldatetime']
                timeSch = data['results'][i]['scheduledarrivaldatetime']

                timeArr = timeArr.split(" ")[1]
                timeSch = timeSch.split(" ")[1]
                FMT = "%H:%M:%S"

                delay = (datetime.datetime.strptime(timeSch, FMT) - datetime.datetime.strptime(timeArr, FMT)).total_seconds()

                times.append([timeArr, delay])
                i+=1

            return times
        else:
            return None
    else:
        return None

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

            # Call live info from RTPI API
            # Returns list of lists with 2 items each. [[bustime, delay],..]
            live_info = getLiveBusInfo(fromVar, busNum)
            next_arrivals = []
            if live_info is not None:
                for x in live_info:
                    next_arrivals.append(live_info[0])
                delay = live_info[0][1]
                bus1 = live_info[0][0]
                if len(live_info)>1:  bus2 = live_info[1][0]
                else: bus2 = ''
                if len(live_info) > 2:  bus3 = live_info[2][0]
                else: bus3 = ''
            else:
                delay = 0
                bus1,bus2,bus3 = 'No upcoming buses', '', ''

            # Retrieve events
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            dayEvents = events[date]
            secondary_term, primary_term, trinity, ucd, bank_holiday, event = dayEvents[0], dayEvents[1], dayEvents[2], dayEvents[3], dayEvents[4], dayEvents[5]

            # call the machine learning function & parse the returned seconds into hours, minutes & seconds.
            journeyTimeSeconds = predictor_ann_improved(ann_improved=ann_improved,
                                                        start_stop=start_stop,
                                                        end_stop=end_stop,
                                                        time_of_day=time_of_day,
                                                        weatherCode=weather,
                                                        secondary_school=secondary_term,
                                                        primary_school=primary_term,
                                                        trinity=trinity,
                                                        ucd=ucd,
                                                        bank_holiday=bank_holiday,
                                                        event=event,
                                                        day_of_year=dayOfYear,
                                                        weekday=weekDay,
                                                        delay=delay)

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s']) # get rid of trailing floating point for seconds.


            # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'onthego.html', {'busNum' : busNum,
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime' : journeyTime,
                                                    #'cost' : cost,
                                                    #'bestStartTime' : bestStartTime})
                                                    'bus1': bus1,
                                                    'bus2': bus2,
                                                    'bus3': bus3,
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
                                                           'date': dateVar,
                                                           'time': timeVar,
                                                            'error': 1}) #Error code > 0 means something bad happened...

            # Retrieve events
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            dayEvents = events[date]
            secondary_term, primary_term, trinity, ucd, bank_holiday, event = dayEvents[0], dayEvents[1], dayEvents[
                2], dayEvents[3], dayEvents[4], dayEvents[5]

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
                                                        delay=0)  # 0 for future dates

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s'])  # get rid of trailing floating point for seconds.


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
                                                   'date': dateVar,
                                                   'time': timeVar,
                                                    'error': 0})  # 0 means everything good


            #return HttpResponse("Bus Num: "+busNum+"<br>"+"From: "+fromVar+"<br>"+"To: "+toVar+"<br>"+"Date: "+str(dateVar)+"<br>"+"Time: "+str(timeVar)) #FOR DEBUGGING

        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")

# Function to get timetable information in the future
def getTimetableInfo(stop_id, route_id, day_time):

    # # NOTE date time for URL must be in the format 'YYYY-MM-DDTHH:mm:ss' ISO format.
    # datetime = datetime.isoformat()
    #
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/timetableinformation?operator=bac&type=week&"
                     "stopid="+stop_id+"&routeid="+route_id+"&format=json")
    if r.status_code == requests.codes.ok:
        data = json.loads(r.content)
        day = day_time.weekday()
        # Find timetable for Monday to Friday
        if day>=0 and day<=4:
            timetable = data['results'][1]['departures']
        # Saturday
        elif day == 5:
            timetable = data['results'][1]['departures']
        # Sunday
        elif day == 6:
            timetable = data['results'][1]['departures']

        # Convert input time to seconds
        input_time = day_time.hour*3600 + day_time.minute*60

        # Convert timetable times to seconds
        timetable_seconds = [(int(x.split(':')[0])*3600 + int(x.split(':')[1])*60) for x in timetable]

        # Find index of closest time
        i_time = min(range(len(timetable_seconds)), key=lambda i: abs(timetable_seconds[i] - input_time))

        return timetable[i_time]

    else:
        return null


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
