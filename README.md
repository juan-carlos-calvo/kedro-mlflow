# Kedro-MLFlow

| Theme | Status |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `main` Branch Build | [![CircleCI](https://circleci.com/gh/juan-carlos-calvo/kedro-mlflow/tree/main.svg?style=shield&circle-token=2535d520b7500278174c6e2ae36fee594231ea9b)](https://circleci.com/gh/juan-carlos-calvo/kedro-mlflow/tree/main) |
| License | [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) |
| Code Style | [![Code Style: Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/ambv/black) |


MLflow is an open source platform for managing the end-to-end machine learning lifecycle. It tackles four primary functions:

- Tracking experiments to record and compare parameters and results (MLflow Tracking).

- Packaging ML code in a reusable, reproducible form in order to share with other data scientists or transfer to production (MLflow Projects).

- Managing and deploying models from a variety of ML libraries to a variety of model serving and inference platforms (MLflow Models).

- Providing a central model store to collaboratively manage the full lifecycle of an MLflow Model, including model versioning, stage transitions, and annotations (MLflow Model Registry).


## How do I install Kedro-MLFlow?

Kedro-MLFlow is a Kedro plugin. To install it:
```bash
git clone
```

```bash
pip install -e .
```

## How do I use Kedro-MLFlow?

By default you'll start logging your parameters. To specify which kedro datasets to log, please create specify the configuration in your parameters file.

### `parameters.yml` configuration

Here is an example of a configuration to start logging datasets, plots, metrics, and models:

```yaml
kedro_mlflow:
  params: ["a"] # if not specified, it will log all parameters. Otherwise, it will log those whose names are listed here.
  datasets: ["preprocessed_shuttles"] # These datasets will get logged as artifacts.
  models: # Here you can specify which models to log, these will get logged as mlflow models.
    regressor: # name of the kedro dataset
      name: regressor # optional. Name of the model on mlflow
      input: X_train # optional. For serving, you can specify a sample input to your model to create a signature for the model serving api
```

## Can I contribute?

Yes! Want to help build Kedro-MLFlow? Check out our guide to [contributing](https://github.com/quantumblacklabs/kedro-docker/blob/develop/CONTRIBUTING.md).

## What licence do you use?

Kedro-Docker is licensed under the [Apache 2.0](https://github.com/quantumblacklabs/kedro-docker/blob/develop/LICENSE.md) License.
