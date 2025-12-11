# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from nvflare.apis.dxo import DXO, DataKind, from_shareable
from nvflare.apis.signal import Signal

from logistic_regression_quickstart.model.executor import TrainingExecutor


@pytest.fixture
def mock_signal():
    """Fixture to mock Signal."""
    return MagicMock(spec=Signal, triggered=False)


@pytest.fixture
def executor():
    """Fixture to create an instance of TrainingExecutor."""
    return TrainingExecutor(cohorts={})


def test_execute(fl_ctx, mock_signal, executor, tmp_path_app_root, mocker):
    """Test execute method with task_name 'run'."""

    mocker.patch(
        "logistic_regression_quickstart.model.executor.download_dataset",
        return_value={"whas1_gateway-1_org-1": Path("test_path")},
    )
    coeff = np.array([1, 2])
    s = DXO(DataKind.WEIGHTS, {"coeff": coeff}).to_shareable()
    result = executor.execute("run", s, fl_ctx, mock_signal)

    assert from_shareable(result).data == {"coeff": coeff}
