from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils.insert_data import push_data_to_db

default_args = {
    "owner": "Alex",
    "depends_on_past": False,
    "retries": 1,
    "email_on_failure": False,
    "retry_delay": timedelta(minutes = 5)
}

# create a DAG for the initialisation pipeline
with DAG(
    dag_id = "dag_postgres_upload",
    default_args = default_args,
    start_date = datetime.now(),
    schedule_interval = timedelta(days = 10)
) as dag:
    # Create tables for the dataset, metadata tables for the operators and the pipeline and a metadata table for model information
    create_fuel_efficiency_table = PostgresOperator(
        task_id = 'create_fuel_efficiency_table',
        postgres_conn_id = 'postgres_default',
        sql = "sql/fuel_efficiency_schema.sql"
    )

    fuel_model_metadata_schema = PostgresOperator(
        task_id = 'fuel_model_metadata_schema',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/fuel_model_metadata_schema.sql', 
    )

    pipeline_metadata = PostgresOperator(
        task_id = 'pipeline_metadata',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/pipeline_metadata.sql'
    )

    model_training_dnn_metadata = PostgresOperator(
        task_id = 'model_training_dnn_metadata',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/model_training_dnn_schema.sql'
    )

    model_training_baseline_metadata = PostgresOperator(
        task_id = 'model_training_baseline_metadata',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/model_training_baseline_schema.sql'
    )

    model_evaluation_metadata = PostgresOperator(
        task_id = 'model_evaluation_metadata',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/model_evaluation_schema.sql'
    )

    preprocessing_metadata = PostgresOperator(
        task_id = 'preprocessing_metadata',
        postgres_conn_id = 'postgres_default',
        sql = 'sql/preprocessing_operator_schema.sql'
    )

    insert_data_fuel_efficiency_table = PythonOperator(
        task_id = 'insert_data_fuel_efficiency_table',
        python_callable = push_data_to_db
    )

    [create_fuel_efficiency_table, fuel_model_metadata_schema, model_evaluation_metadata, model_training_baseline_metadata, model_training_baseline_metadata, pipeline_metadata, preprocessing_metadata] >> insert_data_fuel_efficiency_table