DROP TABLE IF EXISTS model_metadata;

CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    model_training_date TIMESTAMP NOT NULL,
    train_loss NUMERIC NOT NULL,
    test_loss NUMERIC NOT NULL,
    no_epochs NUMERIC NOT NULL,
    number_of_layers NUMERIC NOT NULL,
    number_of_neurons_per_layer NUMERIC NOT NULL,
    kernel_initializer VARCHAR(50),
    kernel_regularizer VARCHAR(50),
    val_split NUMERIC NOT NULL,
    loss_metric VARCHAR(50) NOT NULL,
    optimizer VARCHAR(50),
    learning_rate NUMERIC NOT NULL,
    comparison_to_base VARCHAR(50) NOT NULL,
    model_type VARCHAR(255) NOT NULL
);