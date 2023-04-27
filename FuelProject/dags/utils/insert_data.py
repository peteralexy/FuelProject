import psycopg2
import requests
import pandas as pd

# data URL
URL = 'http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data'

def push_data_to_db():
    """
        Inserts data from the given URL to Postgres
    """
    column_names = ['MPG', 'Cylinders', 'Displacement', 'Horsepower', 'Weight',
                'Acceleration', 'Model_Year', 'Origin']
    
    # check to see if the URL exists
    try:
        raw_data = requests.get(URL)

        data = raw_data.text
        # separate name of the car from the relevant data needed to do the modelling
        data = [row.split("\t")[0].split() for row in data.split("\n")]
        # replace ? with None for insertions into postgres
        data = pd.DataFrame(data, columns = column_names)\
            .dropna()\
            .replace("?", None)\
            .reset_index()\
            .rename(columns = {
                'index': 'id'
            })
        # create a unique ID for each record
        data['id'] = data['id'] + 1
    except requests.exceptions.HTTPError as err:
        print(error)

    # set up connection
    connection = psycopg2.connect(
        host = "postgres",
        database = "postgres",
        user = "airflow",
        password = "airflow"
    )

    try:
        cursor = connection.cursor()

        sql_tuples = [tuple(x) for x in data.to_numpy()]
        # use mogrify to format the query in order to insert it in the database
        args = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", tupl).decode("utf-8") for tupl in sql_tuples)
        cursor.execute("INSERT INTO fuel_efficiency VALUES " + (args) + "ON CONFLICT DO NOTHING;")

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()