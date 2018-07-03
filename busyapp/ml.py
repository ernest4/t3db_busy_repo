import pickle
import pandas as pd
from sklearn.externals import joblib
import datetime

from busy.settings import STATIC_ROOT

#testing pickle

test_list = ['one', '2', 'three']

#writing pickle
#with open("./ml_models/test_file",'wb') as outputFile:
#    pickle.dump(test_list, outputFile)

#loading pickle
#with open("./ml_models/test_file", 'rb') as inputFile:
#    loaded_list = pickle.load(inputFile)

#print(loaded_list)

#using joblib as more efficient model loading for scikit models
def predictor(busNum, start_stop, end_stop, weatherCode):
    regr = joblib.load(STATIC_ROOT+'/ml_models/firstprediction.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

    #time of day since midnight in seconds
    now = datetime.datetime.now() + datetime.timedelta(minutes=60) #time of day since epoch + 1h correction for linux server
    #time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    time_of_day = 50000 #TESTING

    start = {'progrnumber':start_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    end = {'progrnumber':end_stop, 'actualtime': time_of_day, 'weather_code': weatherCode}
    index = [0]

    start_df = pd.DataFrame(data=start, index=index)
    end_df = pd.DataFrame(data=end, index=index)


    # Needed to arrange columns in correct order
    start_df = start_df[['progrnumber','actualtime', 'weather_code']]
    end_df = end_df[['progrnumber','actualtime', 'weather_code']]

    startPrediction = regr.predict(start_df)
    endPredicion = regr.predict(end_df)

    # Estimated time
    time_est = endPredicion - startPrediction

    return time_est

#TESTING CASE
#predictor(1,1,20,803) #Should output: 2503 seconds