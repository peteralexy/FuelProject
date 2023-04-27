DROP TABLE IF EXISTS preprocessing_meta;
-- create preprocessing operator
CREATE TABLE IF NOT EXISTS preprocessing_meta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR NOT NULL,
    owner VARCHAR NOT NULL,
    email VARCHAR,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    retries NUMERIC NOT NULL,
    retry_delay INTERVAL NOT NULL
);