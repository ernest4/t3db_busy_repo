import requests
import datetime
import os

#get weather information
hourSinceLastCall = 0 # type: float
weatherCode = 0 # type: int
futureWeatherCodes = []
def getWeather(timeStamp: int = None):
    global hourSinceLastCall
    global weatherCode

    #Dublin id for open weather: 7778677
    def fetchRealTimeWeatherCode(timeStamp: int = None):

        if timeStamp is None: #Default to providing current weather
            r = requests.get('http://api.openweathermap.org/data/2.5/weather',
                             params={'q': 'dublin', 'APPID': os.environ.get('APPID')})

            if r.status_code == requests.codes.ok:
                weatherData = r.json()
                weatherCode = weatherData['weather'][0]['id']
                return weatherCode
            else:
                #Could not get weather
                #Use 'typical' Irish weather, i.e. '801, few clouds'
                return 801
        else: #Make a forecast based on provided timestamp
            r = requests.get('http://api.openweathermap.org/data/2.5/forecast',
                             #params={'id': '7778677', 'APPID': os.environ.get('APPID')})
                             params={'id': '7778677', 'APPID': ''})  # DO NOT COMMIT, DO NOT PUSH !!!!!!

            # DO NOT COMMIT, DO NOT PUSH !!!!!!
            # DO NOT COMMIT, DO NOT PUSH !!!!!!
            # DO NOT COMMIT, DO NOT PUSH !!!!!!

            if r.status_code == requests.codes.ok:
                weatherData = r.json()

                #weatherCode = weatherData['weather'][0]['id']

                #Check the cache....

                futureWeatherCodes = [] #Empty the list
                for row in weatherData['list']:
                    print(row['dt'],':',row['weather'][0]['id'])

                    #Pupulate the cache
                    futureWeatherCodes.append({'dt': row['dt'], 'id': row['weather'][0]['id']})

                weatherCode = 1010
                return weatherCode
            else:
                # Could not get weather
                # Use 'typical' Irish weather, i.e. '801, few clouds'
                return 801


    #if app just started up...
    if hourSinceLastCall == 0:
        hourSinceLastCall = datetime.datetime.now() + datetime.timedelta(minutes=60)
        weatherCode = fetchRealTimeWeatherCode()
        weatherCodeReturned = weatherCode

    # else query OpenWeather API every hour
    currentCallTime = datetime.datetime.now()
    if currentCallTime > hourSinceLastCall:
        hourSinceLastCall = currentCallTime + datetime.timedelta(minutes=60)
        #cache the weather code
        weatherCode = fetchRealTimeWeatherCode()
        weatherCodeReturned = weatherCode


    # else query OpenWeather 5 day forecast API every 3 hours if timestamp provided

    #if currentCallTime > hourSinceLastCall and timeStamp is not None:
    if timeStamp is not None:
        hourSinceLastCall = currentCallTime + datetime.timedelta(minutes=60)
        #cache the weather code
        futureWeatherCode = fetchRealTimeWeatherCode(timeStamp)
        weatherCodeReturned = futureWeatherCode

    return weatherCodeReturned

print(getWeather(1533114780)) # Tuesday, 1 August 2018 09:13:00 GMT