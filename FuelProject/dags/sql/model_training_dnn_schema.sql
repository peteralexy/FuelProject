DROP TABLE IF EXISTS training_dnn_metadata;

CREATE TABLE IF NOT EXISTS training_dnn_metadata(
    id SERIAL PRIMARY KEY,
    task_id VARCHAR NOT NULL,
    owner VARCHAR NOT NULL,
    email VARCHAR,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    retries NUMERIC NOT NULL,
    retry_delay INTERVAL NOT NULL
)