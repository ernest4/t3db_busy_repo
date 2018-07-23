import pickle
import pandas as pd
import requests
import os
import datetime
import json
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
hourSinceLastCall = 0
weatherCode = 0
def getWeather():
    global hourSinceLastCall
    global weatherCode

    def fetchRealTimeWeatherCode():
        r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                         params={'q': 'dublin', 'APPID': os.environ.get('APPID')})
        weatherData = r.json()
        weatherCode = weatherData['weather'][0]['id']
        return weatherCode

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

def getNormalizedWeather():
    return getWeather()/804 #Max weather code value is 804

def getNormalizedDayOfYear():
    now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
    year2018inSeconds = 1514764800 #seconds since epoch till January 1st 2018
    startOfYear = datetime.datetime.utcfromtimestamp(year2018inSeconds)
    ratio = (startOfYear - now).total_seconds()
    return ratio

def secondsSinceMidnight():
    now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
    time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return time_of_day

def secondsNormalizedSinceMidnight():
    return secondsSinceMidnight()/86400

def getWeekDayBinaryArray():
    weekDay = [0, 0, 0, 0, 0, 0, 0]  # Binary representation of the 7 days of the week
    indexOfToday = datetime.datetime.today().weekday()
    weekDay[indexOfToday] = 1
    return weekDay


#using joblib as more efficient model loading for scikit models
def predictor_svm(busNum, start_stop, end_stop, time_of_day, weatherCode, testing=False):
    if testing:
        svm = joblib.load('static/ml_models/46A_SVM.pkl')
    else:
        svm = joblib.load(STATIC_ROOT+'/ml_models/46A_SVM.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

    start = {'progrnumber':start_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    end = {'progrnumber':end_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    index = [0]

    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)


    # Needed to arrange columns in correct order
    start_df = start_df[['progrnumber','actualtime', 'weather_code']]
    end_df = end_df[['progrnumber','actualtime', 'weather_code']]

    startPrediction = svm.predict(start_df)
    endPredicion = svm.predict(end_df)

    # Estimated time
    print(startPrediction)
    print(endPredicion)
    time_est = endPredicion - startPrediction

    return time_est[0]


def predictor_ann(busNum, start_stop, end_stop, time_of_day, weatherCode, testing=False):
    if testing:
        svm = joblib.load('static/ml_models/NNmodel.pkl')
    else:
        svm = joblib.load(STATIC_ROOT+'/ml_models/NNmodel.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

    start = {'progrnumber':start_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    end = {'progrnumber':end_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    index = [0]

    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)


    # Needed to arrange columns in correct order
    start_df = start_df[['progrnumber','actualtime', 'weather_code']]
    end_df = end_df[['progrnumber','actualtime', 'weather_code']]

    startPrediction = svm.predict(start_df)
    endPredicion = svm.predict(end_df)

    # Estimated time
    print(startPrediction)
    print(endPredicion)
    time_est = endPredicion - startPrediction

    return time_est[0]


def predictor_regression(busNum, start_stop, end_stop, time_of_day, weatherCode, testing=False):
    if testing:
        regr = joblib.load('static/ml_models/firstprediction.pkl')
    else:
        regr = joblib.load(STATIC_ROOT+'/ml_models/firstprediction.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

    start = {'progrnumber':start_stop, 'actualtime': time_of_day}
    end = {'progrnumber':end_stop, 'actualtime': time_of_day}
    index = [0]

    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)


    # Needed to arrange columns in correct order
    start_df = start_df[['progrnumber','actualtime']]
    end_df = end_df[['progrnumber','actualtime']]

    startPrediction = regr.predict(start_df)
    endPredicion = regr.predict(end_df)

    # Estimated time
    time_est = endPredicion - startPrediction

    return time_est[0]


def getModelAndProgNum(busNum, busDirection, start_stop, end_stop, testing):
    # To uppercase
    busNum = busNum.upper()

    if testing:
        routesFileString = 'static/bus_data/routes.json'
    else:
        routesFileString = STATIC_ROOT+'/bus_data/routes.json'

    with open(routesFileString) as f:
        data = json.load(f)

        try:
            # Match bus direction 'I' / 1 inbound, 'O' / 2 outbound
            if busDirection in data[busNum]['I'][1]:
                direction = '1'
                start_prog_num = getProgrNumb(data, busNum, 'I', start_stop)
                end_prog_num = getProgrNumb(data, busNum, 'I', end_stop)

            elif busDirection in data[busNum]['O'][1]:
                direction = '0'
                start_prog_num = getProgrNumb(data, busNum, 'O', start_stop)
                end_prog_num = getProgrNumb(data, busNum, 'O', end_stop)

            file = busNum + '_' + direction  # replace busDirection with direction when not testing

        except:
            return

    if testing:
        return joblib.load('static/ml_models/' + file + '.pkl'), start_prog_num, end_prog_num, float(direction)
    else:
        return joblib.load(STATIC_ROOT+'/ml_models/' + file + '.pkl'), start_prog_num, end_prog_num, float(direction)


def getProgrNumb(data, busNum, direction, stop_id):
    # Return program number + 1 as index in model file names starts with 1
    try:
        return data[busNum][direction][0]['stop' + str(stop_id)][0] + 1
    except:
        return


def predictor_ann_improved(busNum, busDirection, start_stop, end_stop, time_of_day, weatherCode, secondary_school, primary_school, trinity, ucd, bank_holiday, event, day_of_year, weekday, testing=False):
    #Fetch the right model
    ann_improved, start_stop, end_stop, busDirection = getModelAndProgNum(busNum, busDirection, start_stop, end_stop, testing)

    #Abort if model could not be found
    if ann_improved is None:
        return -1

    #Normalize values
    start_stop = start_stop/59
    end_stop = end_stop/59

    start = {'secondary_school': secondary_school,
             'primary_school': primary_school,
             'trinity': trinity,
             'ucd': ucd,
             'bank_holiday': bank_holiday,
             'event': event,
             'progrnumber': start_stop,
             'actualtime': time_of_day,
             'day_of_year': day_of_year,
             'weather_code': weatherCode,
             'mon': weekday[0],
             'tue': weekday[1],
             'wed': weekday[2],
             'thu': weekday[3],
             'fri': weekday[4],
             'sat': weekday[5],
             'sun': weekday[6],
             'starting_stop': 0}

    end = {'secondary_school': secondary_school,
             'primary_school': primary_school,
             'trinity': trinity,
             'ucd': ucd,
             'bank_holiday': bank_holiday,
             'event': event,
             'progrnumber': end_stop,
             'actualtime': time_of_day,
             'day_of_year': day_of_year,
             'weather_code': weatherCode,
             'mon': weekday[0],
             'tue': weekday[1],
             'wed': weekday[2],
             'thu': weekday[3],
             'fri': weekday[4],
             'sat': weekday[5],
             'sun': weekday[6],
             'starting_stop': 0}
    index = [0]

    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)


    # Needed to arrange columns in correct order
    start_df = start_df[['secondary_school',
                         'primary_school',
                         'trinity',
                         'ucd',
                         'bank_holiday',
                         'event',
                         'progrnumber',
                         'actualtime',
                         'day_of_year',
                         'weather_code',
                         'mon',
                         'tue',
                         'wed',
                         'thu',
                         'fri',
                         'sat',
                         'sun',
                         'starting_stop']]

    end_df = end_df[['secondary_school',
                         'primary_school',
                         'trinity',
                         'ucd',
                         'bank_holiday',
                         'event',
                         'progrnumber',
                         'actualtime',
                         'day_of_year',
                         'weather_code',
                         'mon',
                         'tue',
                         'wed',
                         'thu',
                         'fri',
                         'sat',
                         'sun',
                         'starting_stop']]

    startPrediction = ann_improved.predict(start_df)
    endPredicion = ann_improved.predict(end_df)

    # Estimated time
    print(startPrediction)
    print(endPredicion)
    time_est = endPredicion - startPrediction

    return time_est[0]*16397 #multiply to convert from normalized to real seconds