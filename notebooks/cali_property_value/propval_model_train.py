# Databricks notebook source
# MAGIC %md
# MAGIC # `model_train`
# MAGIC Pipeline to execute model training. Params, metrics and model artifacts will be tracked to MLflow Tracking.
# MAGIC Optionally, the resulting model will be registered to MLflow Model Registry if provided.

# COMMAND ----------
# DBTITLE 1,Set env
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment Name")

# COMMAND ----------
# DBTITLE 1,Module Imports
from src.common import Table
from src.utils.notebook_utils import load_and_set_env_vars, load_config
from src.mlops.model_train import (
    ModelTrain,
    ModelTrainConfig,
    MLflowTrackingConfig,
)
from src.model_pipelines.random_forest import RandomForestPipelines
from src.mlops.evaluation_utils import RegressionEvaluation
from src.mlops.plot_utils import PlotGenerator

# COMMAND ----------
# DBTITLE 1,Load Config
# Load env vars from config file (`conf/env_name/` dir)
env_vars = load_and_set_env_vars(env=dbutils.widgets.get("env"))

# Load pipeline config from config file (`conf/pipeline_config/` dir)
pipeline_config = load_config(
    pipeline_name="propval_model_train_cfg",
)

# COMMAND ----------
# DBTITLE 1,Setup Pipeline Config
train_table = Table(
    catalog=env_vars["catalog"], schema=env_vars["property_schema"], table=env_vars["propval_train_table"]
)

model_pipeline = RandomForestPipelines.simple_rf_regressor(model_params=pipeline_config["model_params"])
model_evaluation = RegressionEvaluation()
# plot_generator = PlotGenerator(model_type="regression")
plot_generator = None

mlflow_tracking_cfg = MLflowTrackingConfig(
    run_name=pipeline_config["mlflow_params"]["run_name"],  # TODO: change to random name?
    experiment_path=env_vars["propval_model_train_exper_path"],
    model_name=env_vars["propval_model_name"],
)

model_train_cfg = ModelTrainConfig(
    mlflow_tracking_cfg=mlflow_tracking_cfg,
    train_table=train_table,
    label_col=env_vars["propval_label_col"],
    model_pipeline=model_pipeline,
    model_params=pipeline_config["model_params"],  # For logging with model
    preproc_params=pipeline_config["preproc_params"],
    model_evaluation=model_evaluation,
    plot_generator=plot_generator,
    conf=pipeline_config,
    env_vars=env_vars,
)

# COMMAND ----------
# DBTITLE 1,Execute Pipeline
model_train = ModelTrain(cfg=model_train_cfg)
model_train.run()
