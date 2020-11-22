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
from typing import Any, Dict

import mlflow
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from mlflow.models.signature import infer_signature

from .config_model import MLFlowLoggerConfig
from .log_helpers import get_first_element

logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class MLFlowLogger:
    """Kedro Hook for logging to MLFlow.
    """

    config: MLFlowLoggerConfig = None
    run_id: str = None

    @hook_impl
    def after_catalog_created(self, catalog: DataCatalog) -> None:
        """gets params, initializes logger, and logs params.
        """
        logger.info("Initializing mlflow logger")
        logger.info(__package__)

        params = catalog.load("parameters")
        self.config = MLFlowLoggerConfig(**params)
        if self.config.enabled:
            self._log_params()

    def _log_params(self):
        with mlflow.start_run(run_id=self.run_id) as run:
            self.run_id = run.info.run_id or self.run_id
            logger.info("Logging params")
            mlflow.log_params(self.config.params)

    @hook_impl
    def after_node_run(self, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """inspects inputs and outputs and logs according to internal config.
        """
        for output in outputs:
            if output in self.config.models:
                self._log_model(output, outputs, inputs)

    def _get_signature_and_example(self, model_name, inputs, model):
        model_config = self.config.models[model_name]
        if model_config.input in inputs:
            input_example_el = get_first_element(inputs[model_config.input])
            signature = infer_signature(
                input_example_el, model.predict(input_example_el)
            )
        else:
            input_example_el = None
            signature = None
        return signature, input_example_el

    def _log_model(self, model_name, outputs, inputs):
        model = outputs[model_name]
        signature, example = self._get_signature_and_example(model_name, inputs, model)
        with mlflow.start_run(run_id=self.run_id):
            logger.info("logging model with input example %s", example)
            mlflow.sklearn.log_model(
                model,
                self.config.models[model_name].name,
                signature=signature,
                input_example=example,
            )


hooks = MLFlowLogger()
