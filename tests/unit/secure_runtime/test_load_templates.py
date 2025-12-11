# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path

from logistic_regression_quickstart.secure_runtime.loaders import (
    load_client_config,
    load_server_config,
)
from logistic_regression_quickstart.secure_runtime.payload import (
    LogisticRegressionPayload,
)


def testload_client_config(mocker, tmp_path: Path):
    # Create a mock payload object with some fake data
    payload = LogisticRegressionPayload(task_id="train", cohorts={}, num_rounds=2)

    # Call the function to be tested
    config = load_client_config(payload)

    # Check that the config has been populated correctly with data from the payload
    assert config["executors"][0]["tasks"] == ["train"]


def testload_server_config(mocker, tmp_path: Path):
    # Create a mock payload object with some fake data
    payload = LogisticRegressionPayload(task_id="train", cohorts={}, num_rounds=2)

    # Call the function to be tested
    config = load_server_config(payload, num_clients=2)

    # Check that the config has been populated correctly with data from the payload
    assert config["workflows"][0]["id"] == "scatter_and_gather"
