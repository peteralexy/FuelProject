DELETE FROM model_metadata ver1 
USING model_metadata ver2
WHERE ver1.id < ver2.id AND ver1.model_type = ver2.model_type;