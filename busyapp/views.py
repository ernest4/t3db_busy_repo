from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import numpy as np
import os
import datetime
import json
import pytz
import csv
import json
import googlemaps

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

def about(request):
    return render(request, 'about.html') 

def tourist(request):
    return render(request, 'tourist.html')

def accessibility(request):
    return render(request, 'accessibility.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

def routeInfo(request):
    params = request.GET;
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/routeinformation?format=json",
                     params={'operator': params['operator'],
                             'routeid': params['routeid']})
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)

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


def busRoutesAutosuggest(request):
    with open(STATIC_ROOT+'/bus_data/routes.json', 'r') as file:
        return HttpResponse(file.read())


#Function for RTPI querying for Route Number Autosuggests.
def routeNumberAutosuggest(request):
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/routelistinformation")
    if r.status_code == requests.codes.ok:
        return HttpResponse(r.text)


def loadTest(request):
    with open(STATIC_ROOT+'/load_testing/loaderio-66417165d8f4c651a7a4a33b4dd4c867.txt', 'r', encoding="utf8") as file:
        return HttpResponse(file.read())


def testView(request):
    #r = request.GET;
    #return render(request, 'testpage.html', {'msg1' : r['t']})
    return render(request, 'hi')


def testView2(request):
    return render(request, 'onthego_response.html', {'busNum': 5, 'error': 0})


def personas(request):
    return render(request, "personas.html")



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

                timeFmt = datetime.datetime.strptime(timeArr, FMT).strftime('%H:%M')

                times.append([timeFmt, delay])
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
                return render(request, 'response.html', {'persona': 'onthego',
                                                         'busNum': busNum,
                                                        'from': fromVar,
                                                        'to': toVar,
                                                        'error_1': errorMSG,
                                                        'error_2': errorMSG2,
                                                        'error_3': errorMSG3,
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
            journeyTime['h'], journeyTime['m'],journeyTime['s'] = int(journeyTime['h']), int(journeyTime['m']),int(journeyTime['s'])


            # server side rendering of the response html
            return render(request, 'response.html', {'persona': 'onthego',
                                                     'busNum' : busNum.upper(),
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime' : journeyTime,
                                                     #'journeyTime': journeyTimeSeconds,
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

            # Seconds since the epoch till the input date
            inputDateTimeStamp = int(datetime.datetime(dateVar.year, dateVar.month, dateVar.day, timeVar.hour, timeVar.minute, timeVar.second, tzinfo=datetime.timezone.utc).timestamp())
            weather = getWeather(inputDateTimeStamp) #TESTING, CREATE getFutureWeather() FUNCTION IN THE FUTURE....

            dayOfYear = (datetime.datetime(dateVar.year, dateVar.month, dateVar.day, tzinfo=datetime.timezone.utc)
                       - datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)).total_seconds()

            weekDay = getWeekDayBinaryArray(datetime.datetime(dateVar.year, dateVar.month, dateVar.day, tzinfo=datetime.timezone.utc).weekday())


            # Fetch the right model
            ann_improved, start_stop, end_stop = getModelAndProgNum(busNum, fromVar, toVar, weekdayIndex=datetime.datetime.today().weekday())

            if ann_improved is None:  # Model could not be retrieved
                # server side rendering - replace with AJAX for client side rendering in the future
                errorMSG = "Oops something went wrong :/"
                errorMSG2 = "The combination of route and stops you have entered may not be valid \
                            and/or may not be in service on this particular weekday."
                errorMSG3 = "Please check your inputs and try again."
                return render(request, 'response.html', {'persona': 'planner',
                                                            'busNum': busNum.upper(),
                                                            'from': fromVar,
                                                            'to': toVar,
                                                            'journeyTime': errorMSG,
                                                            'cost': errorMSG2,
                                                            'bestStartTime': errorMSG3,
                                                           'date': dateVar,
                                                           'time': timeVar,
                                                            'error': 1}) #Error code > 0 means something bad happened...

            # Retrieve events
            date = datetime.datetime.strftime(dateVar, "%Y-%m-%d")
            dayEvents = events[date]
            secondary_term, primary_term, trinity, ucd, bank_holiday, event = dayEvents[0], dayEvents[1], dayEvents[
                2], dayEvents[3], dayEvents[4], dayEvents[5]

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
                                                        delay=0)  # 0 for future dates

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['h'], journeyTime['m'],journeyTime['s'] = int(journeyTime['h']), int(journeyTime['m']),int(journeyTime['s'])
              # get rid of trailing floating point for seconds.
            #journeyTime['s'] = round(journeyTime['s'])  # get rid of trailing floating point for seconds.


            #bestStartTime = datetime.datetime.now() + datetime.timedelta(minutes=60)  # note 1h addition for linux servers

            # Find best time to travel

            bus_timetable_seconds, bus_timetable, index = getTimetableInfo(fromVar, busNum, time_of_day, dateVar)

            # Set quickest time to inf so comparison is valid at first run
            # Timetables return None if there are no buses. Need to check for this
            if bus_timetable_seconds != None:
                quickestTime = np.inf
                for i in range(len(bus_timetable_seconds)):
                    # Only take values that are within 1 hour of time.
                    if bus_timetable_seconds[i] <= time_of_day-3600 or bus_timetable_seconds[i] >= time_of_day+3600:
                        continue

                    journeyTimeSecondsB = predictor_ann_improved(ann_improved=ann_improved,
                                                                start_stop=start_stop,
                                                                end_stop=end_stop,
                                                                time_of_day=bus_timetable_seconds[i],
                                                                weatherCode=weather,
                                                                secondary_school=secondary_term,
                                                                primary_school=primary_term,
                                                                trinity=trinity,
                                                                ucd=ucd,
                                                                bank_holiday=bank_holiday,
                                                                event=event,
                                                                day_of_year=dayOfYear,
                                                                weekday=weekDay,
                                                                delay=0)
                    # Compare to see if journey is the quickest
                    if journeyTimeSecondsB < quickestTime:
                        quickestTime = journeyTimeSecondsB
                        bestTime = bus_timetable[i][:-3]


                # If best time is 20% or greater than 5 minutes quicker suggest time.
                if (quickestTime <= (journeyTimeSeconds*0.8) or (journeyTimeSeconds-quickestTime) > 300) and journeyTimeSeconds-quickestTime>60:
                    # If time is over an hour
                    if quickestTime/3600>1:
                        quickestTime = str(int(quickestTime/3600)) + "hrs"+str(int((quickestTime%3600) / 60)) + " mins"
                    # If time is in minutes
                    elif quickestTime/60>1:
                        quickestTime = str(int(quickestTime/60)) + " minutes"
                    else:
                        quickestTime = str(int(quickestTime)) + " seconds"
                else:
                    quickestTime = None
                    bestTime = "You have chosen the quickest time to travel in this period"

            else:
                quickestTime = None
                bestTime = "There are no buses at this time"

            if bus_timetable != None:
                leaveTime = bus_timetable[index][:-3]
            else:
                leaveTime = None

            # Get time in standard 24hr format
            timeVar = timeVar.strftime("%H:%M")


                # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'response.html', {'persona': 'planner',
                                                     'busNum': busNum.upper(),
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'journeyTime': journeyTime,
                                                    'leave_time': leaveTime,
                                                    'bestStartTime': bestTime,
                                                    'bestJourneyTime': quickestTime,
                                                   'date': dateVar,
                                                   'time': timeVar,
                                                    'error': 0})  # 0 means everything good

        else:
            return HttpResponse("Oops! Form invalid :/ Try again?" + form.cleaned_data['time_var'])

# Function to get timetable information in the future
def getTimetableInfo(stop_id, route_id, day_time, date):

    #day_time in seconds, date in datetime format


    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/timetableinformation?operator=bac&type=week&"
                     "stopid="+stop_id+"&routeid="+route_id+"&format=json")
    if r.status_code == requests.codes.ok:
        data = json.loads(r.content)
        day = date.weekday()

        # Find timetable for Monday to Friday (This is a join of Monday-Sunday and Monday-Friday)
        if day>=0 and day<=4:
            # Mon-Friday combines two sets
            timetable = set(data['results'][1]['departures'])
            timetable = timetable.union(set(data['results'][0]['departures']))
        # Saturday
        elif day == 5:
            timetable = set(data['results'][2]['departures'])
        # Sunday
        elif day == 6:
            timetable = set(data['results'][0]['departures'])

        # Convert back to ordered liist
        time_list = list(timetable)
        time_list.sort()

        # Convert timetable time_list to seconds
        timetable_seconds = [(int(x.split(':')[0])*3600 + int(x.split(':')[1])*60) for x in time_list]

        # Find index of closest time
        i_time = min(range(len(timetable_seconds)), key=lambda i: abs(timetable_seconds[i] - day_time))

        # Initiate 2 lists for time in HH:MM and another for seconds
        tsecs=[]
        times=[]

        for i, x in enumerate(timetable_seconds):
            if x > day_time-3600 and x < day_time+3600:
                tsecs.append(x)
                times.append(time_list[i])

        if len(tsecs)>0:
            i_time = min(range(len(tsecs)), key=lambda i: abs(tsecs[i] - day_time))

            return tsecs, times, i_time
        else:
            return None, None, None

    else:
        return None, None, None


def touristform(request):

    if request.method == 'GET':
        form = TouristForm(request.GET)

        #Prefered way of handling forms, validate first before using.
        if form.is_valid():
            fromVar = form.cleaned_data['from_var_ex'].split(',')[0]
            toVar = form.cleaned_data['to_var_ex'].split(',')[0]
            dateVar = form.cleaned_data['date_var_ex']
            timeVar = form.cleaned_data['time_var_ex']

            # Get timestamp in seconds for Google directions request
            whenVar = int(datetime.datetime(dateVar.year, dateVar.month, dateVar.day, timeVar.hour, timeVar.minute, timeVar.second, tzinfo=datetime.timezone.utc).timestamp())


            # This HAS TO BE removed before committing
            gmaps = googlemaps.Client(key='AIzaSyD6np6k3fgrKMPsQuDFFFdcTaBNmE-iGXU')

            # Request directions via public transit
            directions_result = gmaps.directions(fromVar,
                                     toVar)
            #                          mode="transit",
            #                          departure_time=whenVar)

            # Get time in standard 24hr format
            timeVar = form.cleaned_data['time_var_ex'].strftime("%H:%M")

            return render(request, 'response.html', {'persona': 'explorer',
                                                    'from': fromVar,
                                                    'to': toVar,
                                                    'date': dateVar,
                                                    'time': timeVar,
                                                    'directions': directions_result,
                                                    'error': 0})  # 0 means everything good
        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")

# def tourist_directions(request):
#     if request.method == 'POST':
#
#         # Get directions result
#         # result = json.load(sys.stdin)
#         result = json.load(request)
#         jsonResponse = json.dump(result, sys.stdout, indent=2)
#
#         return HttpResponse(jsonResponse)


def plannerform_loadtest(request):
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

            # Seconds since the epoch till the input date
            inputDateTimeStamp = int(datetime.datetime(dateVar.year, dateVar.month, dateVar.day, timeVar.hour, timeVar.minute, timeVar.second, tzinfo=datetime.timezone.utc).timestamp())
            weather = getWeather(inputDateTimeStamp) #TESTING, CREATE getFutureWeather() FUNCTION IN THE FUTURE....

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
                return render(request, 'response.html', {'persona': 'planner',
                                                         'busNum': busNum,
                                                         'from': fromVar,
                                                         'to': toVar,
                                                         'journeyTime': errorMSG,
                                                         'cost': errorMSG2,
                                                         'bestStartTime': errorMSG3,
                                                         'date': dateVar,
                                                         'time': timeVar,
                                                         'error': 1}) #Error code > 0 means something bad happened...

            # Retrieve events
            date = datetime.datetime.strftime(dateVar, "%Y-%m-%d")
            dayEvents = events[date]
            secondary_term, primary_term, trinity, ucd, bank_holiday, event = dayEvents[0], dayEvents[1], dayEvents[
                2], dayEvents[3], dayEvents[4], dayEvents[5]

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
                                                        delay=0)  # 0 for future dates

            journeyTime = {'h': 0, 'm': 0, 's': 0}
            journeyTime['m'], journeyTime['s'] = divmod(journeyTimeSeconds, 60)
            journeyTime['h'], journeyTime['m'] = divmod(journeyTime['m'], 60)
            journeyTime['s'] = round(journeyTime['s'])  # get rid of trailing floating point for seconds.


            bestStartTime = datetime.datetime.now() + datetime.timedelta(minutes=60)  # note 1h addition for linux servers

            # Find best time to travel

            timeStart = time_of_day - 3600
            quickestTime = np.inf
            for x in range(13):
                # Add 10min (600s) every iteration
                time = timeStart + 600*x
                journeyTimeSecondsB = predictor_ann_improved(ann_improved=ann_improved,
                                                            start_stop=start_stop,
                                                            end_stop=end_stop,
                                                            time_of_day=time,
                                                            weatherCode=weather,
                                                            secondary_school=secondary_term,
                                                            primary_school=primary_term,
                                                            trinity=trinity,
                                                            ucd=ucd,
                                                            bank_holiday=bank_holiday,
                                                            event=event,
                                                            day_of_year=dayOfYear,
                                                            weekday=weekDay,
                                                            delay=0)
                if journeyTimeSecondsB < quickestTime:
                    quickestTime = journeyTimeSecondsB
                    bestTime = time

            if bestTime == time_of_day:
                timeNorm = "You have chosen the quickest time to travel in this period"
                journeyTimeB = ''

            else:
                timeNorm = str(datetime.timedelta(seconds=bestTime))
                journeyTimeB = {'h': 0, 'm': 0, 's': 0}
                journeyTimeB['m'], journeyTimeB['s'] = divmod(quickestTime, 60)
                journeyTimeB['h'], journeyTimeB['m'] = divmod(journeyTimeB['m'], 60)
                journeyTimeB['s'] = round(journeyTimeB['s'])  # get rid of trailing floating point for seconds.

            bus_timetable = getTimetableInfo(fromVar, busNum, time_of_day, dateVar)


                # server side rendering - replace with AJAX for client side rendering in the future
            return render(request, 'response.html', {'persona': 'planner',
                                                     'busNum': busNum,
                                                     'from': fromVar,
                                                     'to': toVar,
                                                     'journeyTime': journeyTime,
                                                     # 'cost' : cost,
                                                     # 'bestStartTime' : bestStartTime})
                                                     'leave_time': bus_timetable,
                                                     'bestStartTime': timeNorm,
                                                     'bestJourneyTime': journeyTimeB,
                                                     'date': dateVar,
                                                     'time': timeVar,
                                                     'error': 0})  # 0 means everything good

        else:
            return HttpResponse("Oops! Form invalid :/ Try again?")
