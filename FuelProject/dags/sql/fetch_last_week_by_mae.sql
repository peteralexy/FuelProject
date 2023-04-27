SELECT model_metadata.model_type, model_metadata.model_training_date, model_metadata.test_loss
FROM model_metadata
WHERE model_metadata.model_training_date > (NOW() - interval '7 days') AND model_metadata.test_loss <= 2.5 AND model_metadata.loss_metric = 'mean_absolute_error';