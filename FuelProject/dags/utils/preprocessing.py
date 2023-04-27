import psycopg2
import pandas as pd
import numpy as np
import tensorflow as tf

def preprocess_data(**kwargs):
    """
        Preprocessing the data and saving it to the local data folder
    """

    config = kwargs['dag_run'].conf

    connection = psycopg2.connect(
        host = "postgres",
        database = "postgres",
        user = "airflow",
        password = "airflow"
    )
    try:
        cursor = connection.cursor()

        # get all data
        cursor.execute("SELECT * FROM fuel_efficiency")
        data = cursor.fetchall()
        col_names = [descritpion[0] for descritpion in cursor.description]
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
    dataset = pd.DataFrame(data, columns = col_names)

    dataset = dataset.dropna()

    # do data validation
    assert dataset.isnull().sum().sum() == 0

    assert dataset.shape[1] > 0

    assert dataset['origin'].max() == 3

    assert (dataset.min() >= 0).all()

    old_dataset_columns_number = dataset.shape[1]

    # one-hot encode categorical values
    dataset["origin"] = dataset['origin'].map({1: 'USA', 2: 'Europe', 3: 'Japan'})
    dataset = pd.get_dummies(dataset, columns=['origin'], prefix='', prefix_sep='')

    # 3 new columns, losing origin
    assert dataset.shape[1] == old_dataset_columns_number - 1 + 3

    # split the data into 80-20 and keep 20% of it for evaluation purposes
    train_dataset = dataset.sample(frac=0.8, random_state = 0)
    test_dataset = dataset.drop(train_dataset.index)

    # save the data locally since it fits into memory
    train_dataset.to_csv("/opt/airflow/data/train.csv", index = False)
    test_dataset.to_csv("/opt/airflow/data/test.csv", index = False)