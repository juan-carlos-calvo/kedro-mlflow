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

""" config model and parsers """

from typing import Any, Dict, List

from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    ValidationError,
    root_validator,
)


class ModelToLog(BaseModel):  # pylint: disable=too-few-public-methods
    """info for model to be logged"""

    name: str
    input: str = None


class MLFlowLoggerConfig(BaseModel):
    """config for mlflow logger"""

    enabled: bool = True
    params: Dict[str, Any]
    models: Dict[str, ModelToLog] = {}
    metrics: List[str] = []
    artifacts: List[str] = []
    tags: Dict[str, Any] = {}

    @root_validator(pre=True)
    def parse_config(cls, params):  # pylint: disable=no-self-use, no-self-argument
        """parse config to right format"""
        config = parse_params(params)
        return parse_models(config)


def parse_params(params):
    """parse kedro_mlflow config from params"""
    if __package__ not in params:
        return {"params": params}
    config = params.pop(__package__)
    assert isinstance(config, dict), "params:kedro_mlflow must be a dictionary or None"
    if "params" not in config:
        config["params"] = params
    else:
        selection = config["params"]
        assert isinstance(selection, list), "params:kedro_mlflow.params must be a list"
        config["params"] = {
            name: value for name, value in params.items() if name in selection
        }
    return config


def parse_models(config):
    """Parse config to get models in right format"""
    if "models" not in config:
        return config
    models = config["models"]
    if isinstance(models, list):
        models = {model: {"name": model} for model in models}
    elif isinstance(models, dict):
        res = {}
        for model, spec in models.items():
            spec["name"] = spec.get("name") or model
            res[model] = spec
        models = res
    else:
        raise ValidationError
    config["models"] = models
    return config
