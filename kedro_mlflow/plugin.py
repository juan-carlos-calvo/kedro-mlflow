# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

""" Kedro plugin for logging to mlflow """

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import mlflow
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from mlflow.models.signature import infer_signature

from .helpers import get_first_element

logger = logging.getLogger(__name__)

TO_BE_LOGGED = ["params", "datasets", "models"]


@dataclass(unsafe_hash=True)
class MLFlowLogger:  # pylint: disable=too-many-instance-attributes
    """Kedro Hook for logging to MLFlow.
    """

    to_be_logged = TO_BE_LOGGED
    supported_models = [""]
    enabled: bool = True
    # artifacts_to_log: List[str] = None
    datasets_to_log: List[str] = None
    params_to_log: Dict[str, Any] = None
    models_to_log: Dict[str, dict] = None
    project_params: Dict[str, Any] = None
    run_id: str = None

    @hook_impl
    def after_catalog_created(self, catalog: DataCatalog) -> None:
        """gets params, initializes logger, and logs params.
        """
        logger.info("Initializing mlflow logger")
        logger.info(__package__)

        params = catalog.load("parameters")
        self.set_config(params)
        if self.enabled:
            self._log_params()

    def set_config(self, params):
        """updates the logger properties according to config on `params`"""
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
    def after_node_run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """inspects inputs and outputs and logs according to internal config.
        """
        for output in outputs:
            if output in self.models_to_log:
                self._log_model(output, inputs, outputs)

    def _log_model(self, model_name, inputs, outputs):
        with mlflow.start_run(run_id=self.run_id):
            model = outputs[model_name]
            input_example = self.models_to_log[model_name].get("input")
            log_name = self.models_to_log[model_name].get("name") or model_name
            if input_example in inputs:
                input_example_el = get_first_element(inputs[input_example])
                signature = infer_signature(
                    input_example_el, model.predict(input_example_el)
                )
            else:
                input_example_el = None
                signature = None
            logger.info("logging model with input example %s", input_example)
            mlflow.sklearn.log_model(
                model, log_name, signature=signature, input_example=input_example_el
            )


hooks = MLFlowLogger()
