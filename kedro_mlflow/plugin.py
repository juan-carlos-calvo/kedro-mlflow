import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

import mlflow
import numpy as np
import pandas as pd
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from kedro.pipeline.node import Node
from mlflow.models.signature import infer_signature

logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class MLFlowLogger:
    to_be_logged = ["params", "datasets", "models"]
    supported_models = [""]
    enabled: bool = True
    # artifacts_to_log: List[str] = None
    datasets_to_log: List[str] = None
    params_to_log: Dict[str, Any] = None
    models_to_log: Dict[str, dict] = None
    project_params: Dict[str, Any] = None
    run_id: str = None

    @hook_impl
    def after_catalog_created(
        self, catalog: DataCatalog
    ) -> None:  # pylint: disable=unused-argument
        logger.info("Initializing mlflow logger")
        logger.info(__package__)

        params = catalog.load("parameters")
        self._set_config(params)
        if self.enabled:
            self._log_params()

    def _set_config(self, params):
        spec = params.get(__package__)
        self._set_enabled(spec)
        if spec is not None:
            for to_log in self.to_be_logged:
                setattr(self, f"{to_log}_to_log", spec.get(to_log))
        del params[__package__]
        self.project_params = params

    def _set_enabled(self, spec):
        enabled = spec.get("enabled")
        self.enabled = enabled if enabled is not None else self.enabled

    def _log_params(self):
        if self.params_to_log is None:
            to_log = self.project_params
        else:
            to_log = {
                param: value
                for param, value in self.project_params.items()
                if param in self.params_to_log
            }
        with mlflow.start_run(run_id=self.run_id) as run:
            self.run_id = run.info.run_id or self.run_id
            logger.info("Logging params")
            mlflow.log_params(to_log)

    @hook_impl
    def after_node_run(
        self, node: Node, inputs: Dict[str, Any], outputs: Dict[str, Any]
    ):
        for output in outputs:
            if output in self.models_to_log:
                self._log_model(output, inputs, outputs)

    def _log_model(self, model_name, inputs, outputs):
        with mlflow.start_run(run_id=self.run_id) as run:
            model = outputs[model_name]
            input_example = self.models_to_log[model_name].get("input")
            log_name = self.models_to_log[model_name].get("name") or model_name
            if input_example in inputs:
                input_example_el = self.get_first_element(inputs[input_example])
                signature = infer_signature(
                    input_example_el, model.predict(input_example_el)
                )
            else:
                input_example_el = None
                signature = None
            logger.info(f"logging model with input example {input_example}")
            mlflow.sklearn.log_model(
                model, log_name, signature=signature, input_example=input_example_el
            )

    def get_first_element(self, array: Union[pd.DataFrame, np.ndarray]):
        if isinstance(array, pd.DataFrame):
            array = array.iloc[0].values
        return array[:1]


hooks = MLFlowLogger()
