DROP TABLE IF EXISTS pipeline_metadata;

CREATE TABLE IF NOT EXISTS pipeline_metadata(
    id SERIAL PRIMARY KEY,
    dag_id VARCHAR NOT NULL,
    owner VARCHAR NOT NULL,
    email VARCHAR,
    retries NUMERIC NOT NULL,
    retry_delay INTERVAL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    task_count NUMERIC NOT NULL,
    schedule_interval INTERVAL
)