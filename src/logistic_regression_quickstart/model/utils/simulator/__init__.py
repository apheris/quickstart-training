# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path
from typing import List

from nvflare.private.fed.app.simulator.simulator_runner import SimulatorRunner


def run_flare_simulator(
    job_folder: Path,
    workspace_path: Path,
    clients: List[str],
):
    """
    Run the NVIDIA FLARE simulator with the given job configs and workspace.
    """
    job_folder = job_folder.resolve()
    if not job_folder.is_dir():
        raise FileNotFoundError(
            "The path to the job directory appears to be incorrect. Aborting"
        )
    workspace_path = workspace_path.resolve()
    if not workspace_path.is_dir():
        raise FileNotFoundError(
            "The path to the workspace directory appears to be incorrect. Aborting"
        )

    simulator = SimulatorRunner(
        job_folder=str(job_folder),
        workspace=workspace_path,
        clients=",".join(clients),
        n_clients=len(clients),
        threads=len(clients),
        gpu=None,
        max_clients=len(clients),
    )
    run_status = simulator.run()
    return run_status


__all__ = [
    "run_flare_simulator",
]
