import pickle
import pandas as pd
from sklearn.externals import joblib
from datetime import datetime

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
def predictor(busNum, start_stop, end_stop):
    regr = joblib.load(STATIC_ROOT+'/ml_models/firstprediction.pkl')

    #start_stop = #convert input start stop...read the raw program number for now...
    #end_stop = #convert input end stop...read the raw program number for now...

    #time of day since midnight in seconds
    now = datetime.now() + datetime.timedelta(minutes=60) #time of day since epoch + 1h correction for linux server
    time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

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

    return time_est