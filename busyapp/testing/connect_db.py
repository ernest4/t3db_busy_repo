import psycopg2
import psycopg2.extras
import os


def test_db_connect():
    # Connect to db
    DATABASE_URL = 'postgres://wjsijzcxzxlrjv:7ffab95e34aa03daf1f86b7b09746b77e3ecb5ec686c400ab5e98182e4562e28@ec2-54-83-3-101.compute-1.amazonaws.com:5432/dfb6d81u4nkjvn'

    conn = psycopg2.connect(DATABASE_URL)

    # Open a (dictionary) cursor to perform db operation
    # For documentation: http://initd.org/psycopg/docs/extras.html
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute a command: this creates a new table
    # Should return 46a in direction 0 with stops 810 and 2795 as prognum 4 and 23
    cur.execute("SELECT * FROM stops WHERE route_id = '{0}';".format('46A'))

    # Obtain data as Python object
    result = cur.fetchone() #one line only, even if the query returns multiple records.
    #result = cur.fetchone() #multiple results, returns all the records from the query.

    # Print result in various ways...
    print(result)
    print(result['id'])
    print(result['route_id'])

    for index, value in enumerate(result):
        print('index: ',index,' value: ',value,' program number: ',index-5)

    cur.close()
    conn.close()

test_db_connect() #TESTING