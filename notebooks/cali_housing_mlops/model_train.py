# Databricks notebook source
# MAGIC %md
# MAGIC # `model_train`
# MAGIC
# MAGIC Pipeline to execute model training. Params, metrics and model artifacts will be tracked to MLflow Tracking.
# MAGIC Optionally, the resulting model will be registered to MLflow Model Registry if provided.

# COMMAND ----------
# DBTITLE 1,Install requirements
# MAGIC %pip install -r ../../requirements.txt

# COMMAND ----------
# DBTITLE 1,Set env
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment Name")

# COMMAND ----------
# DBTITLE 1,Module Imports
from databricks_common.common import MetastoreTable
from src.utils.notebook_utils import load_and_set_env_vars, load_config
from src.mlops.model_train import (
    ModelTrain,
    ModelTrainConfig,
    MLflowTrackingConfig,
)
from src.model_pipelines.cali_housing_pipeline import CaliHousingPipeline

# COMMAND ----------
# DBTITLE 1,Load Config
# Load env vars from config file (`conf/env_name/` dir)
env_vars = load_and_set_env_vars(env=dbutils.widgets.get("env"))

# Load pipeline config from config file (`conf/pipeline_config/` dir)
pipeline_config = load_config(
    pipeline_name="model_train_cfg",
    project="cali_housing_mlops",
)

# COMMAND ----------
# DBTITLE 1,Setup Pipeline Config
mlflow_tracking_cfg = MLflowTrackingConfig(
    run_name=pipeline_config["mlflow_params"]["run_name"],
    experiment_path=env_vars["cali_train_exper_path"],
    model_name=env_vars["cali_model_name"],
)

train_table = MetastoreTable(
    catalog=env_vars["cali_catalog"],
    schema=env_vars["cali_schema"],
    table=env_vars["cali_train_table"],
)

model_pipeline = CaliHousingPipeline.create_rf_pipeline_v2(model_params=pipeline_config["model_params"])

model_train_cfg = ModelTrainConfig(
    mlflow_tracking_cfg=mlflow_tracking_cfg,
    train_table=train_table,
    label_col=env_vars["cali_label_col"],
    model_pipeline=model_pipeline,
    model_params=pipeline_config["model_params"],  # For logging with model
    preproc_params=pipeline_config["preproc_params"],
    conf=pipeline_config,
    env_vars=env_vars,
)

# COMMAND ----------
# DBTITLE 1,Execute Pipeline
model_train = ModelTrain(cfg=model_train_cfg)
model_train.run()
