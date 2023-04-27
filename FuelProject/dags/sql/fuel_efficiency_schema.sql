DROP TABLE IF EXISTS fuel_efficiency;
-- create fuel efficiency table
CREATE TABLE IF NOT EXISTS fuel_efficiency (
    id SERIAL PRIMARY KEY,
    mpg NUMERIC(6, 1) NOT NULL,
    cylinders NUMERIC(6, 1),
    displacement NUMERIC(6, 1),
    horsepower NUMERIC(6, 1),
    weight NUMERIC(6, 1),
    acceleration NUMERIC(6, 1),
    model_year NUMERIC(6, 1),
    origin NUMERIC(6, 1)
);