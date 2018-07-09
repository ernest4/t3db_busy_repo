import pickle
import pandas as pd
import requests
import os
from sklearn.externals import joblib
import datetime

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

def predictor_ann_improved(busNum, start_stop, end_stop, time_of_day, weatherCode, secondary_school, primary_school, trinity, ucd, bank_holiday, event, day_of_year, weekday, testing=False):
    if testing:
        ann_improved = joblib.load('static/ml_models/NNmodelEVENTS.pkl')
    else:
        ann_improved = joblib.load(STATIC_ROOT+'/ml_models/NNmodelEVENTS.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

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
             'mon': weekday['mon'],
             'tue': weekday['tue'],
             'wed': weekday['wed'],
             'thu': weekday['thu'],
             'fri': weekday['fri'],
             'sat': weekday['sat'],
             'sun': weekday['sun'],
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
             'mon': weekday['mon'],
             'tue': weekday['tue'],
             'wed': weekday['wed'],
             'thu': weekday['thu'],
             'fri': weekday['fri'],
             'sat': weekday['sat'],
             'sun': weekday['sun'],
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

    return time_est[0]*16397