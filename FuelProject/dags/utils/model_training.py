import json
import pandas as pd
import tensorflow as tf
import os
import numpy as np


def train_baseline(**kwargs):
    """
        Training a baseline linear model
    """

    if kwargs['dag_run'].conf != {}:
        config = kwargs['dag_run'].conf
    else:
        with open("dags/utils/config.json", "r") as f:
            config = json.load(f)

    # if the model exists do nothing
    if not os.path.exists('/opt/airflow/models/baseline'):

        train_dataset = pd.read_csv("/opt/airflow/data/train.csv").drop("id", axis = 1)
        train_features = train_dataset.astype(np.float32).copy()

        train_labels = train_features.pop('mpg')

        normalizer = tf.keras.layers.Normalization(axis = -1)
        normalizer.adapt(np.array(train_features))

        baseline_model = tf.keras.Sequential([
            normalizer,
            tf.keras.layers.Dense(units = 1)
        ])


        baseline_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate = config['learning_rate']),
            loss=config['loss'])

        baseline_model.fit(
            train_features,
            train_labels,
            epochs=config['epochs'],
            # Suppress logging.
            verbose=0,
            # Calculate validation results on 20% of the training data.
            validation_split = config['validation_split'])
        
        baseline_model.save("/opt/airflow/models/baseline")

def train_dnn(**kwargs):
    """
        Training a DNN model
    """

    if kwargs['dag_run'].conf != {}:
        config = kwargs['dag_run'].conf
    else:
        with open("dags/utils/config.json", "r") as f:
            config = json.load(f)

    # load data
    train_dataset = pd.read_csv("/opt/airflow/data/train.csv").drop("id", axis = 1)
    train_features = train_dataset.astype(np.float32).copy()

    # extract target
    train_labels = train_features.pop('mpg')

    # init normalization layer to standardise the data
    normalizer = tf.keras.layers.Normalization(axis = -1)
    normalizer.adapt(np.array(train_features))

    assert (np.round(normalizer.mean.numpy(), 2) == np.round(train_features.mean().values, 2)).all()

    # create the sequential model
    baseline_model = tf.keras.Sequential(
        [normalizer] + \
        [
            tf.keras.layers.Dense(
                config['neurons'], 
                activation=config['activation'],
                kernel_initializer = config['kernel_initializer'],
                kernel_regularizer = config['kernel_regularizer']
                ) 
            for i in range(config['number_of_layers'])
            ] + \
        [tf.keras.layers.Dense(1)]
    )

    # compile the model
    baseline_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config['learning_rate']),
        loss=config['loss'])

    # train the model
    baseline_model.fit(
        train_features,
        train_labels,
        epochs = config['epochs'],
        # Suppress logging.
        verbose = 0,
        # Calculate validation results on 20% of the training data.
        validation_split = config['validation_split'])

    # save the model
    model_name = f"/opt/airflow/models/dnn_{config['number_of_layers']}_layers_{config['neurons']}_neurons_{config['activation']}_activation"
    if not os.path.exists(model_name):
        baseline_model.save(model_name)