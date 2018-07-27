import psycopg2
import os


def test_db_connect():
    # Connect to db
    DATABASE_URL = 'postgres://wjsijzcxzxlrjv:7ffab95e34aa03daf1f86b7b09746b77e3ecb5ec686c400ab5e98182e4562e28@ec2-54-83-3-101.compute-1.amazonaws.com:5432/dfb6d81u4nkjvn'
    #print(DATABASE_URL)
    #DATABASE_URL = os.environ.get('DATABASE_URL')


    conn = psycopg2.connect(DATABASE_URL)

    # Open a cursor to perform db operation
    cur = conn.cursor()

    # Execute a command: this creates a new table
    # Should return 46a in direction 0 with stops 810 and 2795 as prognum 4 and 23
    cur.execute("SELECT * FROM stops WHERE id = 16680;")

    # Obtain data as Python object
    result = cur.fetchone()

    # Print result
    print(result)

    cur.close()
    conn.close()

#test_db_connect()