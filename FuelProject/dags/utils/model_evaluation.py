import json
import psycopg2
import pandas as pd
import tensorflow as tf
from datetime import datetime

def evaluation(**kwargs):
    # check if parameters were passed down in the DAG execution, if not fall back to some default ones
    if kwargs['dag_run'].conf != {}:
        config = kwargs['dag_run'].conf
    else:
        with open("dags/utils/config.json", "r") as f:
            config = json.load(f)

    # load training and test data
    train_features = pd.read_csv("/opt/airflow/data/train.csv").drop(["id"], axis = 1)
    train_labels = train_features.pop('mpg')

    test_features = pd.read_csv("/opt/airflow/data/test.csv").drop(["id"], axis = 1)
    test_labels = test_features.pop('mpg')

    # load the baseline and dnn models using the config file (last ran model)
    base = tf.keras.models.load_model("/opt/airflow/models/baseline")
    model_path = f"dnn_{config['number_of_layers']}_layers_{config['neurons']}_neurons_{config['activation']}_activation"
    complex = tf.keras.models.load_model(f"/opt/airflow/models/{model_path}")

    # evaluate both models, only comparing the test performance
    base_train_loss = base.evaluate(train_features, train_labels)
    base_test_loss = base.evaluate(test_features, test_labels)

    complex_train_loss = complex.evaluate(train_features, train_labels)
    complex_test_loss = complex.evaluate(test_features, test_labels)

    # flag to see if it is better than a simple regression
    comaprison_flag = "Better" if complex_test_loss < base_test_loss else "Worse"

    # metadata for the current dnn model
    metadata = {
        "model_training_date": datetime.now(),
        "train_loss": complex_train_loss,
        "test_loss": complex_test_loss,
        "no_epochs": config['epochs'],
        "number_of_layers": config['number_of_layers'],
        "number_of_neurons_per_layer": config['neurons'],
        "kernel_initializer": config['kernel_initializer'],
        "kernel_regularizer": config['kernel_regularizer'],
        "val_split": config['validation_split'],
        "loss_metric": config['loss'],
        "learning_rate": config['learning_rate'],
        "comparison_to_base": comaprison_flag,
        "model_type": model_path
    }

    # upload the metadata to the database
    try:
        connection = psycopg2.connect(
            host = "postgres",
            database = "postgres",
            user = "airflow",
            password = "airflow"
        )

        cursor = connection.cursor()

        headers = ', '.join(metadata.keys())
        sql_tuples = [tuple(metadata.values())]

        input_values = '(' + ', '.join(['%s' for i in range(len(metadata.keys()))]) + ')'

        args = ','.join(cursor.mogrify(input_values, tupl).decode("utf-8") for tupl in sql_tuples)
        cursor.execute(f"INSERT INTO model_metadata ({headers}) VALUES " + (args) + "ON CONFLICT DO NOTHING;")

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()