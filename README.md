# End-to-End-Chest-Cancer-Classification-using-MLflow-DVC


## Workflows

1. Update config.yaml
2. Update secrets.yaml [Optional]
3. Update params.yaml
4. Update the entity
5. Update the configuration manager in src config
6. Update the components
7. Update the pipeline 
8. Update the main.py
9. Update the dvc.yaml 






### dagshub

MLflow tracking credentials are not committed to this repo. Create a `.env` file
in the project root (already git-ignored) with:

```
MLFLOW_TRACKING_URI=https://dagshub.com/ayyappathalwar/End-to-End-Chest-Cancer-Classification-using-MLflow-DVC.mlflow
MLFLOW_TRACKING_USERNAME=<your-dagshub-username>
MLFLOW_TRACKING_PASSWORD=<your-dagshub-access-token>
```

Get an access token from https://dagshub.com/user/settings/tokens