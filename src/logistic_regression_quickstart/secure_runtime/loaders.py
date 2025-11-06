# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path

from .payload import LogisticRegressionPayload

TEMPLATE_PATH = Path(__file__).parent


def load_client_config(payload: LogisticRegressionPayload) -> dict:
    """
    Load the FLARE client config template and populate with data from the job payload
    """

    # TODO: Update this with the necessary args for the logistic regression

    return {
        "format_version": 2,
        "executors": [
            {
                "tasks": ["train"],
                "executor": {
                    "path": "logistic_regression_quickstart.model.executor"
                    ".TrainingExecutor",
                    "args": {"cohorts": payload.cohorts},
                },
            }
        ],
        "task_result_filters": [],
        "task_data_filters": [],
        "components": [],
    }


def load_server_config(payload: LogisticRegressionPayload, num_clients: int) -> dict:
    """
    Load the FLARE server config and populate with data from the job payload
    """
    return {
        "format_version": 2,
        "server": {"heart_beat_timeout": 600},
        "task_data_filters": [],
        "task_result_filters": [],
        "workflows": [
            {
                "id": "scatter_and_gather",
                "path": "nvflare.app_common.workflows.scatter_and_gather"
                ".ScatterAndGather",
                "args": {
                    "min_clients": num_clients,
                    "num_rounds": payload.num_rounds,
                    "start_round": 0,
                    "wait_time_after_min_received": 0,
                    "aggregator_id": "aggregator",
                    "persistor_id": "persistor",
                    "shareable_generator_id": "shareable_generator",
                    "train_task_name": "train",
                    "train_timeout": 0,
                },
            },
        ],
        "components": [
            {
                "id": "persistor",
                "path": "nvflare.app_common.np.np_model_persistor.NPModelPersistor",
                "args": {},
            },
            {
                "id": "shareable_generator",
                "path": "nvflare.app_common.shareablegenerators"
                ".full_model_shareable_generator.FullModelShareableGenerator",
                "args": {},
            },
            {
                "id": "aggregator",
                "path": "nvflare.app_common.aggregators"
                ".intime_accumulate_model_aggregator.InTimeAccumulateWeightedAggregator",
                "args": {"expected_data_kind": "WEIGHTS"},
            },
            {
                "id": "log_writer",
                "path": "apheris_utils.extras_nvflare.logging.orchestrator_log_receiver"
                ".OrchestratorLogReceiver",
                "args": {},
            },
        ],
    }


__all__ = [
    "load_client_config",
    "load_server_config",
]
