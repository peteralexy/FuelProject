import psycopg2
from airflow import DAG
import json
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import TaskInstance
from airflow.operators.python import PythonOperator
from airflow.models.dagbag import DagBag
from airflow.models.dagrun import DagRun
from datetime import datetime

def insert_record_in_table(metadata, table):
    """
        Inserts a record into the appropiate metadata table
    """
    try:
        connection = psycopg2.connect(
            host = 'postgres',
            database = 'postgres',
            user = 'airflow',
            password = 'airflow'
        )

        cursor = connection.cursor()
        headers = ', '.join(metadata.keys())
        sql_tuples = [tuple(metadata.values())]

        input_values = '(' + ', '.join(['%s' for i in range(len(metadata.keys()))]) + ')'

        args = ','.join(cursor.mogrify(input_values, tupl).decode("utf-8") for tupl in sql_tuples)
        cursor.execute(f"INSERT INTO {table} ({headers}) VALUES " + (args) + "ON CONFLICT DO NOTHING;")

        connection.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()

def save_metadata_task(**kwargs):
    """
        Save the metadata for a specific task
    """
    # use dagbag to get information about the dag and the currently running tasks
    dag_bag = DagBag()

    preprocess_data_dag = dag_bag.get_dag("dag_train_evaluation_pipeline")
    task = preprocess_data_dag.get_task(kwargs['dag_run'].conf['task'])

    current_time = datetime.now()
    start_date = task.start_date.strftime('%Y-%m-%d %H:%M:%S')
    start_date_new = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

    # relevant metadata
    metadata = {
        "task_id": task.task_id,
        "owner": task.owner,
        "email": task.email,
        "start_date": start_date_new,
        "end_date": current_time,
        "retries": task.retries,
        "retry_delay": task.retry_delay
    }

    insert_record_in_table(metadata, kwargs['dag_run'].conf['table'])


def save_metadata_dag():
    """
        Save metadata for the DAG
    """
    dag_bag = DagBag()
    preprocess_data_dag = dag_bag.get_dag("dag_train_evaluation_pipeline")

    current_time = datetime.now()
    start_date = preprocess_data_dag.start_date.strftime('%Y-%m-%d %H:%M:%S')
    start_date_new = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

    metadata = {
        "dag_id": preprocess_data_dag.dag_id,
        "owner": preprocess_data_dag.__dict__['default_args']['owner'],
        "email": preprocess_data_dag.__dict__['default_args']['email'],
        "retries": preprocess_data_dag.__dict__['default_args']['retries'],
        "retry_delay": preprocess_data_dag.__dict__['default_args']['retry_delay'],
        "start_date": start_date_new,
        "end_date": current_time,
        "task_count": preprocess_data_dag.task_count,
        "schedule_interval": preprocess_data_dag.schedule_interval
    }

    insert_record_in_table(metadata, table = "pipeline_metadata")

default_args = {
    "owner": "Alex",
    "retries": 1
}

with DAG(
    dag_id = "save_metadata_dag",
    default_args = default_args,
    start_date = datetime.now()
) as dag:
    trigger_task = PythonOperator(
        task_id = 'trigger_dag',
        python_callable = save_metadata_dag
    )

    trigger_task

with DAG(
    dag_id = "save_metadata_task",
    default_args = default_args,
    start_date = datetime.now()
) as dag:
    trigger_dag = PythonOperator(
        task_id = 'trigger_task',
        python_callable = save_metadata_task
    )

    trigger_dag