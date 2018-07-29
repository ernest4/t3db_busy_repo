import psycopg2
import psycopg2.extras
import os
import datetime


def test_db_connect():
    # Connect to db
    DATABASE_URL = 'postgres://wjsijzcxzxlrjv:7ffab95e34aa03daf1f86b7b09746b77e3ecb5ec686c400ab5e98182e4562e28@ec2-54-83-3-101.compute-1.amazonaws.com:5432/dfb6d81u4nkjvn'

    conn = psycopg2.connect(DATABASE_URL)

    # Open a (dictionary) cursor to perform db operation
    # For documentation: http://initd.org/psycopg/docs/extras.html
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #TEST INPUTS
    bus = '46A' #expected direction inbound i.e. model 46A_1.pkl
    startStop = '810' #expected program number 4
    startStopProgramNumber = 0
    endStop = 2795  #expected program number 23
    endStopProgramNumber = 0

    #from GTFS
    #"y102p", "0", "0", "0", "0", "0", "1", "0", "20180629", "20180630"
    #"y102q", "0", "0", "0", "0", "1", "0", "0", "20180629", "20180630"
    #"y102f", "1", "1", "1", "1", "1", "0", "0", "20180701", "20180825" .......use this one for current test to get row with id 16680
    #"y102g", "1", "0", "0", "0", "0", "0", "1", "20180701", "20180825"
    #"y102e", "0", "0", "0", "0", "0", "1", "0", "20180701", "20180825"

    indexOfToday = datetime.datetime.today().weekday()
    print(indexOfToday)
    indexOfToday = 4 #HARD CODED VALUE FOR TESTING
    serviceIDs = {"y102p": [0, 0, 0, 0, 0, 1, 0],
                  "y102q": [0, 0, 0, 0, 1, 0, 0],
                  "y102f": [1, 1, 1, 1, 1, 0, 0],
                  "y102g": [1, 0, 0, 0, 0, 0, 1],
                  "y102e": [0, 0, 0, 0, 0, 1, 0]}

    relevantServiceIDs = []

    for serviceID in serviceIDs:
        print(serviceID)
        if serviceIDs[serviceID][indexOfToday] == 1:
            print("Today: ",serviceID," is valid.")
            relevantServiceIDs.append(serviceID)
    print(relevantServiceIDs)

    # Execute a command: this creates a new table
    # Should return 46a in direction 0 with stops 810 and 2795 as prognum 4 and 23
    cur.execute("SELECT * FROM stops WHERE route_id = '{0}';".format(bus))

    # Obtain data as Python object
    #result = cur.fetchone() #one line only, even if the query returns multiple records.
    results = cur.fetchall() #multiple results, returns all the records from the query.

    # Print result in various ways...
    print(results)
    #print(results['id'])
    #print(results['route_id'])

    allRouteInfoFound = False
    for index, result in enumerate(results): #For every row in the returned query
        if allRouteInfoFound:
            break #Found all the info
        startStopProgramNumber = 0
        print('\n\nParsing line with id: ', result['id'],' and serive_id: ',result['service_id'],'\n')
        if result['service_id'] not in relevantServiceIDs: #The row is not valid as it does not contain information relevant to today's date
            print("skipping...")
            continue

        for index, value in enumerate(result): #For every column in the row
            print('index: ', index, ' value: ', value, ' program number: ', index - 5)
            if index > 5 and value is not None:
                if value.endswith(str(startStop)):
                    startStopProgramNumber = index-5
                    continue
                if startStopProgramNumber > 0 and value.endswith(str(endStop)):
                    endStopProgramNumber = index-5
                    # Found all the info
                    allRouteInfoFound = True
                    direction = result['direction_id']+1 #DB -> APP,    0+1 -> 1,     1+1 -> 2
                    break

    print('\nBus: ',bus,' Pickle: ',bus+'_'+str(direction)+'.pkl')
    print('Start Stop: ',startStop,', Program number: ',startStopProgramNumber)
    print('End Stop: ',endStop, ', Program number: ', endStopProgramNumber)

    cur.close()
    conn.close()

test_db_connect() #TESTING