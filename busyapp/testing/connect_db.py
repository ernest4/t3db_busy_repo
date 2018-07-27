import psycopg2


def test_db_connect():
    # Connect to db
    conn = psycopg2.connect("dbname=dfb6d81u4nkjvn user=wjsijzcxzxlrjv")

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

test_db_connect()