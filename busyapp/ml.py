import pickle
import pandas as pd
import requests
import os
import datetime
import json
import time
import psycopg2
from pprint import pprint
from sklearn.externals import joblib

from busy.settings import STATIC_ROOT

#testing pickle

#test_list = ['one', '2', 'three']

#writing pickle
#with open("./ml_models/test_file",'wb') as outputFile:
#    pickle.dump(test_list, outputFile)

#loading pickle
#with open("./ml_models/test_file", 'rb') as inputFile:
#    loaded_list = pickle.load(inputFile)

#print(loaded_list)

#get weather information
hourSinceLastCall = 0 # type: float
weatherCode = 0 # type: int
def getWeather():
    global hourSinceLastCall
    global weatherCode

    def fetchRealTimeWeatherCode():
        r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                         params={'q': 'dublin', 'APPID': os.environ.get('APPID')})
        if r.status_code == requests.codes.ok:
            weatherData = r.json()
            weatherCode = weatherData['weather'][0]['id']
            return weatherCode
        else:
            return None #Could not get weather

    #if app just started up...
    if hourSinceLastCall == 0:
        hourSinceLastCall = datetime.datetime.now() + datetime.timedelta(minutes=60)
        weatherCode = fetchRealTimeWeatherCode()

    # else query OpenWeather API every hour
    currentCallTime = datetime.datetime.now()
    if currentCallTime > hourSinceLastCall:
        hourSinceLastCall = currentCallTime + datetime.timedelta(minutes=60)
        #cache the weather code
        weatherCode = fetchRealTimeWeatherCode()

    return weatherCode

"""
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
                delay = (datetime.strptime(timeSch, FMT) - datetime.strptime(timeArr, FMT)).total_seconds()

                times+=(timeArr, delay)
                i+=1
            return times
        else:
            return null

# Function to get timetable information in the future
def getTimetableInfo(stop_id, route_id, datetime):

    # NOTE date time for URL must be in the format 'YYYY-MM-DDTHH:mm:ss'

    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/timetableinformation?operator=bac&type=week&stopid=768&routeid=46a&format=json")
    if r.status_code == requests.codes.ok:
        data = json.loads(r.content.decode('utf-8'))


# Function to get the events of a certain day
def getEvents(date):
    pass
"""


def getDayOfYear():
    year2018inSeconds = 1514764800 #seconds since epoch till January 1st 2018
    currentTimeOfYear = round(time.time()) - year2018inSeconds
    return currentTimeOfYear


def secondsSinceMidnight():
    now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
    time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return time_of_day


def getWeekDayBinaryArray(weekdayNumber: int = None) -> [int, ...]:
    weekDay = [0, 0, 0, 0, 0, 0, 0]  # Binary representation of the 7 days of the week

    if weekdayNumber is None:
        indexOfToday = datetime.datetime.today().weekday()
        weekDay[indexOfToday] = 1
    else:
        weekDay[weekdayNumber] = 1

    return weekDay


def getModelAndProgNum(busNum: str, start_stop: int, end_stop: int, weekdayIndex: int = None, testing: bool = False) -> (object, int, int):
    '''
    Get the model, start_prog_num (in DB), end_prog_num (in DB)
    based on busNum, start_stop, end_stop & direction (in DB)

    Args:
        busNum: The string identifying the bus number: e.g. 46A
        start_stop: The code identifying the start stop e.g. 810
        end_stop: The code identifying the end stop e.g. 2795
        testing:

    Returns:
        object: the loaded pickle file of the model.
        int: start stop program number
        int: end stop program number

    """
    '''

    # To uppercase
    busNum = busNum.upper()
    start_stop = str(start_stop) #Make sure it's a string if not already
    end_stop = str(end_stop) #Make sure it's a string if not already
    #starting values
    startStopProgramNumber = 0
    endStopProgramNumber = 0
    direction = ''

    if weekdayIndex is None: #No weekday supplied, default to current weekday
        weekdayIndex = datetime.datetime.today().weekday()
    serviceIDs = {"y102p": [0, 0, 0, 0, 0, 1, 0],
                  "y102q": [0, 0, 0, 0, 1, 0, 0],
                  "y102f": [1, 1, 1, 1, 1, 0, 0],
                  "y102g": [1, 0, 0, 0, 0, 0, 1],
                  "y102e": [0, 0, 0, 0, 0, 1, 0]}

    relevantServiceIDs = []

    #Compile a list of service_ids that are valid for current day of week in order to filter out the correct rows in DB
    # e.g. if today was Friday (indexOfToday == 4) then the relevantServiceIDs == ['y102q', 'y102f']
    for serviceID in serviceIDs:
        if serviceIDs[serviceID][weekdayIndex] == 1:
            relevantServiceIDs.append(serviceID)

    # Connect to db
    DATABASE_URL = os.environ.get('DATABASE_URL')  # Get the connection URI string
    conn = psycopg2.connect(DATABASE_URL)

    # Open a (dictionary) cursor to perform db operation
    # For documentation: http://initd.org/psycopg/docs/extras.html
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute a command: this creates a new table
    # Should return 46a in direction 0 with stops 810 and 2795 as prognum 4 and 23
    cur.execute("SELECT * FROM stops WHERE route_id = '{0}';".format(busNum))

    # Obtain data as Python object
    # result = cur.fetchone() #one line only, even if the query returns multiple records.
    results = cur.fetchall()  # multiple results, returns all the records from the query.

    allRouteInfoFound = False
    for index, result in enumerate(results):  # For every row in the returned query
        if allRouteInfoFound:
            break  # Found all the info
        if result['service_id'] not in relevantServiceIDs: #The row is not valid as it does not contain information relevant to today's date
            continue

        startStopProgramNumber = 0
        for index, value in enumerate(result):  # For every column in the row
            if index > 5 and value is not None:
                if value.endswith(start_stop):
                    startStopProgramNumber = index - 5
                    continue
                if startStopProgramNumber > 0 and value.endswith(end_stop):
                    endStopProgramNumber = index - 5
                    # Found all the info
                    allRouteInfoFound = True
                    direction = str(result['direction_id'] + 1)  # DB -> APP,    0+1 -> 1,     1+1 -> 2
                    break

    #Clean up
    cur.close()
    conn.close()

    #Get the pickle and return the values
    file = busNum + '_' + direction + '.pkl' # replace busDirection with direction when not testing

    if testing:
        #Running locally with command => python manage.py runserver localhost:8765
        try:
            modelPickle = joblib.load('static/ml_models_final/' + file)
        except FileNotFoundError:
            return None, None, None
        # If everything OK, return the answers
        return modelPickle, startStopProgramNumber, endStopProgramNumber
    else:
        #Runing on Heroku or locally with command => heroku local web -f Procfile.windows (for windows)
        try:
            modelPickle = joblib.load(STATIC_ROOT+'/ml_models_final/' + file)
        except FileNotFoundError:
            return None, None, None
        # If everything OK, return the answers
        return modelPickle, startStopProgramNumber, endStopProgramNumber


def predictor_ann_improved(ann_improved, start_stop, end_stop, time_of_day, weatherCode, secondary_school, primary_school, trinity, ucd, bank_holiday, event, day_of_year, weekday, delay, testing=False):

    #Abort if model could not be found
    if ann_improved is None:
        return -1

    start ={'prognum': start_stop,
            'time': time_of_day,
            'day_unix': day_of_year,
            'weather_id': weatherCode,
            'Mon': weekday[0],
            'Tue': weekday[1],
            'Wed': weekday[2],
            'Thu': weekday[3],
            'Fri': weekday[4],
            'Sat': weekday[5],
            'Sun': weekday[6],
            'start_stop': 1, #ALWAYS 1
            'secondary':secondary_school,
            'primary':primary_school,
            'trinity':trinity,
            'ucd':ucd,
            'bank_hol': bank_holiday,
            'event':event,
            'delay': delay}

    end = {'prognum': end_stop,
             'time': time_of_day,
             'day_unix': day_of_year,
             'weather_id': weatherCode,
             'Mon': weekday[0],
             'Tue': weekday[1],
             'Wed': weekday[2],
             'Thu': weekday[3],
             'Fri': weekday[4],
             'Sat': weekday[5],
             'Sun': weekday[6],
             'start_stop': 1,  # ALWAYS 1
             'secondary': secondary_school,
             'primary': primary_school,
             'trinity': trinity,
             'ucd': ucd,
             'bank_hol': bank_holiday,
             'event': event,
             'delay': delay}

    index = [0]
    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)

    startPrediction = ann_improved.predict(start_df)
    endPredicion = ann_improved.predict(end_df)

    # Estimated time
    print(startPrediction)
    print(endPredicion)
    time_est = endPredicion - startPrediction

    return time_est[0]
