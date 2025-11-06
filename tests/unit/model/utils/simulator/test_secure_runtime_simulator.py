# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.


import json
from pathlib import Path

from logistic_regression_quickstart.model.utils.simulator.secure_runtime import (
    write_job_configs,
)


def test_write_job_configs(tmp_path: Path):
    config_items = {
        "client1/config/config1.json": {"key1": "value1", "key2": "value2"},
        "server/config/config2.json": {"key3": "value3", "key4": "value4"},
    }

    write_job_configs(tmp_path, config_items)

    with open(tmp_path / "client1/config/config1.json") as fh:
        assert json.load(fh) == {"key1": "value1", "key2": "value2"}

    with open(tmp_path / "server/config/config2.json") as fh:
        assert json.load(fh) == {"key3": "value3", "key4": "value4"}
