import pickle
import pandas as pd
import requests
import os
import datetime
import json
import time
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


def getLiveBusInfo(stop_id, route_id):
    times=[]
    r = requests.get("https://data.dublinked.ie/cgi-bin/rtpi/realtimebusinformation?"
                     "stopid="+stop_id+"&routeid="+route_id+"&maxresults&operator&format=json")
    if r.status_code == requests.codes.ok:
        data = json.loads(r.content.decode('utf-8'))
        if len(data['results']) > 0:
            i = 0
            while i < 3 and i<len(data['results']):
                delay = 
                times+=(data['results'][i]['arrivaldatetime'],
                i+=1
            return times
        else:
            return 'No upcoming buses'



def getNormalizedWeather():
    return getWeather()/804 #Max weather code value is 804


def getDayOfYear():
    year2018inSeconds = 1514764800 #seconds since epoch till January 1st 2018
    currentTimeOfYear = round(time.time()) - year2018inSeconds
    return currentTimeOfYear


def secondsSinceMidnight():
    now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
    time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return time_of_day


def getWeekDayBinaryArray():
    weekDay = [0, 0, 0, 0, 0, 0, 0]  # Binary representation of the 7 days of the week
    indexOfToday = datetime.datetime.today().weekday()
    weekDay[indexOfToday] = 1
    return weekDay


def getModelAndProgNum(busNum, start_stop, end_stop, testing):
    # To uppercase
    busNum = busNum.upper()

    #DATABASE ACCES CODE HERE....

    #Get the model, start_prog_num (in DB), end_prog_num (in DB)
    # based on busNum, start_stop, end_stop & direction (in DB)

    # DATABASE ACCES CODE HERE....
    direction = '2' #FOR TESTING 2 = outbound [1 in database]
    start_prog_num = 1 #FOR TESTING
    end_prog_num = 28 #FOR TESTING

    # DATABASE ACCES CODE HERE....

    file = busNum + '_' + direction  # replace busDirection with direction when not testing

    if testing:
        return joblib.load('static/ml_models_final/' + file + '.pkl'), start_prog_num, end_prog_num
    else:
        return joblib.load(STATIC_ROOT+'/ml_models_final/' + file + '.pkl'), start_prog_num, end_prog_num


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
