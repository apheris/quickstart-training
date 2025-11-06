# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from contextlib import nullcontext

import pytest

from logistic_regression_quickstart.model.utils.simulator import run_flare_simulator


@pytest.mark.parametrize(
    "create_job_dir, create_workspace_dir, expected_error_type, expected_error_msg",
    [
        (True, True, None, None),
        (
            False,
            True,
            FileNotFoundError,
            "The path to the job directory appears to be incorrect. Aborting",
        ),
        (
            True,
            False,
            FileNotFoundError,
            "The path to the workspace directory appears to be incorrect. Aborting",
        ),
    ],
)
def test_run_simulator(
    mocker,
    tmp_path,
    create_job_dir,
    create_workspace_dir,
    expected_error_type,
    expected_error_msg,
):
    mocker.patch("nvflare.private.fed.app.simulator.simulator_runner.SimulatorRunner.run")

    job_path = tmp_path / "job"

    if create_job_dir:
        job_path.mkdir(exist_ok=True, parents=True)

    workspace_path = tmp_path / "workspace"
    if create_workspace_dir:
        workspace_path.mkdir(exist_ok=True, parents=True)

    if expected_error_type:
        ctx = pytest.raises(expected_error_type, match=expected_error_msg)
    else:
        ctx = nullcontext()

    with ctx:
        run_flare_simulator(job_path, workspace_path, ["client1", "client2"])
