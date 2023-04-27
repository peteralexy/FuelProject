# FuelProject

Using airflow a DAG is created that will extract data from a given URL, load it inside Postgres and afterwards preprocess it and use it to train machine learning models, firstly a linear regression will be trained that will serve as a baseline for the more complex models to beat and then push the metadata
of the models into a tabel in order to view their parameters and performance.

# Usage
First we will need to build a docker image for the python application which will provide us with an interactive application
Inside the app folder execute
```bash
cd app
docker-compose up --build -d
docker-compose down
```
After the image is build we switch to our FuelProject
```bash
cd ../FuelProject
docker-compose up --build -d
```
This will take some time to download the necessary images and install the required python libraries

Once the installation is done and all of our containers have started up we will have to configure the Postgres connection inside our Airflow UI

Navigate to 
```
localhost:8080
```
Using the username and password "airflow" we navigate to Admin -> Connections and Add a new Connection with the following configurations

* connection_id: postgres_default
* connection_type: Postgres
* host: postgres
* schema: postgres
* login: airflow
* password: airflow
* port: 5432

After the configuration of the connection is Done, we can access our DAGs tab and run the different possible operations here

* dag_postgres_upload -> will create the schema neede for our dataset and the metadata tabels
* dag_train_evaluation_pipeline -> will run the pipeline where it will collect data from the given URL, save it to postgres, preprocess it and splitting it into a train and a test set and then train a linear regression and a DNN on the training data, evaluating it afterwards on the test set and saving metadata from the training

We can switch to
```
localhost:5000
```
Here a GUI is implemented for end-users to initialise the database themselves with a simple click of a button

1. Database Init and Queries
   * If the database was not initialised the "initialise database" button can be clicked which will start the appropriate DAG
   * We can via the two query buttons either the best models from the past week with a MAE under 2.5 and all the models ever trained
2. Train a DNN
   * Here we can start the pipeline DAG and train a dnn model with custom parameters of our choice

It should be noted that running the machine learning pipeline from the airflow UI on localhost:8080 will use the default parameters specified in 
```/opt/airflow/dags/utils/config.json```

The models are all saved under ```/opt/airflow/models``` and their name represents the configuration of the parameters used

In ```/opt/airflow/dags/testing``` we can execute a file that will test some of the components of the DAG

If metadata from the different operators and the pipeline itself need to be visualised the following steps will followed:
```
docker ps

docker exec -it <container_id_of_the_postgres_instance> bash

psql -U airflow

\c postgres

\dt
```

All the data from the following folders can be deleted since it will be regenerated when the application is ran
```
data/
models/
plugins/
logs/
```

It would be recommended, if the need arises to also see statistics about the baseline, to run the application for a 1 neuron and 1 layers DNN model which
will be the configuration for the baseline