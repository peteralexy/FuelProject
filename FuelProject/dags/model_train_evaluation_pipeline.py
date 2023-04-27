from airflow import DAG
from utils.preprocessing import preprocess_data
from utils.model_training import train_baseline, train_dnn
from utils.model_evaluation import evaluation
from airflow.operators.python import PythonOperator

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    "owner": "Alex",
    "retries": 5,
    "email": "apeter@yahoo.com",
    "retry_delay": timedelta(minutes = 5)
}

# create a dag for the machine learning pipeline
with DAG(
    dag_id = "dag_train_evaluation_pipeline",
    default_args = default_args,
    start_date = datetime.now()
) as dag:
    # preprocessing operator
    preprocessing = PythonOperator(
        task_id = 'preprocess_data',
        python_callable = preprocess_data
    )
    # training a baseline model operator
    train_baseline_op = PythonOperator(
        task_id = 'train_baseline',
        python_callable = train_baseline
    )
    # training a dnn operator
    train_dnn_op = PythonOperator(
        task_id = 'train_dnn',
        python_callable = train_dnn
    )
    # evaluating and saving results to a table operator
    evaluation_op = PythonOperator(
        task_id = 'evaluation',
        python_callable = evaluation
    )

    # define triggers after an operator has finished execution in order to store metadata
    save_preprocess_metadata = TriggerDagRunOperator(
        task_id = 'save_preprocess_metadata',
        trigger_dag_id = 'save_metadata_task',
        conf = {"table": "preprocessing_meta", 'task': 'preprocess_data'}
    )

    save_baseline_metadata = TriggerDagRunOperator(
        task_id = 'save_baseline_metadata',
        trigger_dag_id = 'save_metadata_task',
        conf = {"table": "training_baseline_metadata", 'task': 'train_baseline'}
    )

    save_dnn_metadata = TriggerDagRunOperator(
        task_id = 'save_dnn_metadata',
        trigger_dag_id = 'save_metadata_task',
        conf = {"table": "training_dnn_metadata", 'task': 'train_dnn'}
    )
    
    save_evaluation_metadata = TriggerDagRunOperator(
        task_id = 'save_evaluation_metadata',
        trigger_dag_id = 'save_metadata_task',
        conf = {"table": "evaluation_metadata", 'task': 'evaluation'}
    )

    trigger_dag_metadata = TriggerDagRunOperator(
        task_id = 'metadata_dag',
        trigger_dag_id = 'save_metadata_dag'
    )

    # define execution order
    preprocessing >> save_preprocess_metadata >> [train_baseline_op, train_dnn_op] >> save_baseline_metadata >> save_dnn_metadata >> evaluation_op >> save_evaluation_metadata >> trigger_dag_metadata