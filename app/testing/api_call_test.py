import base64
import json
import requests

username = 'airflow'
password = 'airflow'
auth = base64.b64encode(f"{username}{password}".encode()).decode()

auth = (username, password)

headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

params = {
    "neurons": 64,
    "number_of_layers": 5,
    "validation_split": 0.2,
    "loss": "mean_absolute_error",
    "kernel_initializer": "glorot_uniform",
    "kernel_regularizer": None,
    "activation": "relu",
    "learning_rate": 0.1,
    "epochs": 50
}

url = 'http://localhost:8080//api/v1/dags/dag_train_evaluation_pipeline/dagRuns'
response = requests.post(url, headers=headers, json={"conf": params}, auth = auth)
print(response)
print(response.text)