# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

import apheris_auth
from apheris_utils.extras_nvflare.logging.gateway_log_sender import (
    set_safe_error_handling_enabled,
)
from apheris_utils.extras_simulator.data import configure_env
from model.utils.simulator import run_flare_simulator
from model.utils.simulator.secure_runtime import write_job_configs
from secure_runtime.payload import LogisticRegressionPayload
from secure_runtime.secure_runtime_service import template

sys.path.insert(0, str(Path(__file__).parent.parent))

DEFAULT_SIMULATOR_OUTPUT = (Path.cwd() / "simulator_output").resolve()


logging.basicConfig(level=logging.INFO)


def parse_args(args_list: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the simulator.")
    parser.add_argument(
        "--simulator-output-path",
        type=Path,
        default=DEFAULT_SIMULATOR_OUTPUT,
        help="The path into which we store the simulator workspace and job configs. By "
        "default, this is a folder named 'simulator_output' in the current working "
        "directory.",
    )
    parser.add_argument(
        "--dataset-ids",
        nargs="+",  # Accept one or more values
        type=str,  # Each value is a string
        help="The dataset_ids which identify the development datasets to use in the "
        "simulator. These should be registered in Apheris prior to running the "
        "simulator.",
    )
    # TODO: Add args here as required
    args, _ = parser.parse_known_args(args_list)

    args.simulator_output_path = args.simulator_output_path.resolve()

    args.workspace_path = args.simulator_output_path / "workspace"
    args.jobs_path = args.simulator_output_path / "jobs"

    return args


def main(args: argparse.Namespace):
    """
    Main function to run the simulator.

    Creates a LogisticRegressionPayload object and writes the job configs to the
    specified path. Then calls into the NVIDIA FLARE simulator to actually execute
    the job.

    Outputs are stored in the workspace directory inside the simulator_output folder.
    """

    args.simulator_output_path.mkdir(exist_ok=True, parents=True)
    args.workspace_path.mkdir(exist_ok=True, parents=True)
    args.jobs_path.mkdir(exist_ok=True, parents=True)

    payload = LogisticRegressionPayload(task_id="train", cohorts={})

    dataset_to_gw = {
        dataset_id: f"site-{i+1}" for i, dataset_id in enumerate(args.dataset_ids)
    }

    configs = template(payload, dataset_to_gw)
    write_job_configs(args.jobs_path, configs)

    logging.info(f"Running simulator with job configs in {args.jobs_path}")

    run_status = run_flare_simulator(
        args.jobs_path,
        args.workspace_path,
        list(set(dataset_to_gw.values())),
    )

    if run_status != 0:
        raise RuntimeError(
            f"Simulator run failed. See logs in {args.workspace_path}/simulate_job/"
            "log.txt for more details."
        )

    logging.info(
        f"Simulator run completed successfully. "
        f"Workspace output stored in {args.workspace_path}"
    )


if __name__ == "__main__":

    args = parse_args()

    apheris_auth.login()

    # We'll mock the download behaviour by copying the files into a temporary directory
    # which will serve as the dataset root.
    configure_env(args.dataset_ids)
    set_safe_error_handling_enabled(False)

    main(args)
